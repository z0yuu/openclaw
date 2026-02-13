/**
 * SeaTalk 事件回调：URL 校验、签名校验、单聊消息 -> 跑 Agent 并回发 SeaTalk
 * 路径: POST /api/webhook/seatalk
 * 参考: LLM_minecraft app/api/webhook.py
 *
 * 日志：所有请求与验证结果会打 subsystem "seatalk"，出现在 Gateway 的 stdout/stderr
 * 或 OpenClaw 配置的日志文件中，便于排查「验证不通过」。
 */

import type { IncomingMessage, ServerResponse } from "node:http";
import { randomUUID } from "node:crypto";
import type { CliDeps } from "../cli/deps.js";
import type { CronJob } from "../cron/types.js";
import { loadConfig } from "../config/config.js";
import { runCronIsolatedAgentTurn } from "../cron/isolated-agent.js";
import { createSubsystemLogger } from "../logging/subsystem.js";
import { verifySignature, sendSingleChat } from "./client.js";

const logSeatalk = createSubsystemLogger("seatalk");

/** 支持两种路径（含尾部斜杠）：/api/webhook/seatalk 与 /webhook/seatalk */
const SEATALK_WEBHOOK_PATH_PREFIXES = ["/api/webhook/seatalk", "/webhook/seatalk"];

/** 与可用的 OpenClaw SeaTalk 插件一致：challenge 可能出现的 key 名 */
const CHALLENGE_KEYS = ["seatalk_challenge", "seatalkChallenge", "challenge", "echostr"];

function normalizePath(pathname: string): string {
  return pathname.replace(/\/+$/, "") || "/";
}

function isSeatalkWebhookPath(pathname: string): boolean {
  const normalized = normalizePath(pathname);
  return SEATALK_WEBHOOK_PATH_PREFIXES.some((p) => normalized === p);
}

/** 从任意嵌套的 JSON 对象里递归找 challenge 字符串（与插件 findChallengeInObject 一致） */
function findChallengeInObject(obj: unknown, depth = 0): string | null {
  if (depth > 5) {
    return null;
  }
  if (obj === null || typeof obj !== "object") {
    return null;
  }
  const o = obj as Record<string, unknown>;
  for (const key of CHALLENGE_KEYS) {
    const v = o[key];
    if (typeof v === "string" && v.length > 0) {
      return v;
    }
  }
  for (const v of Object.values(o)) {
    if (typeof v === "object" && v !== null) {
      const found = findChallengeInObject(v, depth + 1);
      if (found) {
        return found;
      }
    }
  }
  return null;
}

/**
 * 从 POST body 解析 seatalk_challenge（支持 JSON 嵌套或 application/x-www-form-urlencoded，与插件一致）
 */
function parseSeatalkChallenge(rawBody: string, contentType: string): string | null {
  const ct = (contentType || "").toLowerCase();
  if (ct.includes("application/json") || rawBody.trim().startsWith("{")) {
    try {
      const body = JSON.parse(rawBody) as Record<string, unknown>;
      const flat = body.seatalk_challenge ?? body.challenge ?? body.echostr;
      if (typeof flat === "string" && flat.length > 0) {
        return flat;
      }
      return findChallengeInObject(body);
    } catch {
      return null;
    }
  }
  if (ct.includes("application/x-www-form-urlencoded") || rawBody.includes("seatalk_challenge=")) {
    try {
      const params = new URLSearchParams(rawBody);
      const v = params.get("seatalk_challenge") ?? params.get("challenge") ?? params.get("echostr");
      return v;
    } catch {
      return null;
    }
  }
  try {
    const body = JSON.parse(rawBody) as Record<string, unknown>;
    return findChallengeInObject(body);
  } catch {
    // ignore
  }
  try {
    const params = new URLSearchParams(rawBody);
    return params.get("seatalk_challenge") ?? params.get("challenge") ?? null;
  } catch {
    return null;
  }
}

function sendJson(res: ServerResponse, status: number, body: unknown) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

function readRawBody(req: IncomingMessage, maxBytes: number): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let total = 0;
    req.on("data", (chunk: Buffer) => {
      total += chunk.length;
      if (total > maxBytes) {
        reject(new Error("SeaTalk webhook body too large"));
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

export type SeaTalkWebhookHandler = (req: IncomingMessage, res: ServerResponse) => Promise<boolean>;

const MAX_BODY_BYTES = 256 * 1024;

/**
 * 创建 SeaTalk 回调处理器，需传入 deps 以便后台跑 Agent。
 */
export function createSeaTalkWebhookHandler(opts: { deps: CliDeps }): SeaTalkWebhookHandler {
  const { deps } = opts;

  return async function handleSeaTalkWebhookRequest(
    req: IncomingMessage,
    res: ServerResponse,
  ): Promise<boolean> {
    const url = new URL(req.url ?? "/", "http://localhost");
    const pathname = url.pathname;
    const normalized = normalizePath(pathname);

    // 任何包含 seatalk 的请求都打一条日志，便于排查「完全没日志」的情况（请求是否到达、路径是否被代理改写）
    if (pathname.includes("seatalk")) {
      logSeatalk.info(`SeaTalk path seen: ${req.method} pathname=${pathname}`);
    }

    if (!isSeatalkWebhookPath(pathname)) {
      return false;
    }

    // 与可用的 OpenClaw SeaTalk 插件一致：先处理 URL 验证（GET/POST），不要求签名
    const rawBodyBuffer = await readRawBody(req, MAX_BODY_BYTES).catch((err) => {
      logSeatalk.warn(`SeaTalk webhook body read error: ${String(err)}`);
      return null;
    });
    if (rawBodyBuffer === null) {
      sendJson(res, 400, { code: 400, message: "Body read error" });
      return true;
    }
    const rawBodyStr = rawBodyBuffer.toString("utf8");
    const contentType = (req.headers["content-type"] as string) ?? "";

    // GET：SeaTalk 可能用 GET + query 做验证，返回 challenge 为 text/plain（与插件一致）
    if (req.method === "GET") {
      const echostr =
        url.searchParams.get("seatalk_challenge") ??
        url.searchParams.get("echostr") ??
        url.searchParams.get("challenge") ??
        url.searchParams.get("msg_signature");
      if (echostr) {
        logSeatalk.info(
          `SeaTalk url verification GET, returning challenge (length=${echostr.length})`,
        );
        res.statusCode = 200;
        res.setHeader("Content-Type", "text/plain; charset=utf-8");
        res.end(echostr);
        return true;
      }
      sendJson(res, 200, {
        message: "SeaTalk webhook endpoint; use POST for event callback.",
        path: normalized,
      });
      return true;
    }

    if (req.method !== "POST") {
      return false;
    }

    logSeatalk.info(`SeaTalk webhook request: POST ${pathname}`);

    // 1. URL 验证（POST）：从 body 或 event_type=event_verification 解析 challenge，先于签名校验（与插件一致）
    const challengeFromBody = parseSeatalkChallenge(rawBodyStr, contentType);
    let body: Record<string, unknown>;
    try {
      body = JSON.parse(rawBodyStr) as Record<string, unknown>;
    } catch {
      body = {};
    }
    const eventType = (body.event_type as string) ?? "";
    const event = body.event as Record<string, unknown> | undefined;
    const challengeFromEvent =
      event && typeof event === "object"
        ? ((event.seatalk_challenge as string | undefined) ??
          (event.challenge as string | undefined))
        : undefined;
    const fromQuery =
      url.searchParams.get("seatalk_challenge") ?? url.searchParams.get("challenge");
    const challenge =
      challengeFromBody ??
      challengeFromEvent ??
      (body.seatalk_challenge as string | undefined) ??
      (body.challenge as string | undefined) ??
      fromQuery ??
      "";

    if (
      eventType === "event_verification" ||
      (typeof challenge === "string" && challenge.length > 0)
    ) {
      const value = typeof challenge === "string" ? challenge : String(challenge);
      if (value.length > 0) {
        logSeatalk.info(
          `SeaTalk url verification, returning challenge (length=${value.length}) event_type=${eventType}`,
        );
        res.statusCode = 200;
        res.setHeader("Content-Type", "application/json; charset=utf-8");
        res.end(JSON.stringify({ seatalk_challenge: value }));
        return true;
      }
      if (eventType === "event_verification") {
        logSeatalk.warn(
          `SeaTalk event_verification but no challenge found; body_len=${rawBodyStr.length} body_preview=${rawBodyStr.slice(0, 280)}`,
        );
      }
    }

    // 2. 签名验证（仅对非 URL 验证的请求校验）
    const signature =
      (req.headers["signature"] as string) ?? (req.headers["Signature"] as string) ?? "";
    if (!verifySignature(rawBodyBuffer, signature)) {
      logSeatalk.warn(
        "SeaTalk webhook signature verification failed (wrong SEATALK_SIGNING_SECRET or body tampered)",
      );
      sendJson(res, 403, { code: 403, message: "Invalid signature" });
      return true;
    }

    logSeatalk.info(`SeaTalk webhook event_type=${eventType}`);

    // 3. 单聊消息等：先快速 200，后台跑 Agent 再回发
    if (eventType === "message_from_bot_subscriber") {
      const event = (body.event as Record<string, unknown>) ?? {};
      const employeeCode = (event.employee_code as string) ?? "";
      const message = (event.message as Record<string, unknown>) ?? {};
      const tag = (message.tag as string) ?? "";
      let textContent = "";
      if (tag === "text") {
        const text = (message.text as Record<string, unknown>) ?? {};
        textContent = ((text.content as string) ?? "").trim();
      }
      if (employeeCode && textContent) {
        setImmediate(() => {
          void handleTextMessage(deps, employeeCode, textContent);
        });
      }
    }

    // 4. 新订阅者可选：发欢迎语（此处不实现，可后续扩展）
    // if (eventType === "new_bot_subscriber") { ... }

    sendJson(res, 200, { code: 0 });
    return true;
  };
}

async function handleTextMessage(
  deps: CliDeps,
  employeeCode: string,
  message: string,
): Promise<void> {
  try {
    const cfg = loadConfig();
    const now = Date.now();
    const job: CronJob = {
      id: randomUUID(),
      name: "seatalk-webhook",
      enabled: true,
      createdAtMs: now,
      updatedAtMs: now,
      schedule: { kind: "at", at: new Date(now).toISOString() },
      sessionTarget: "isolated",
      wakeMode: "now",
      payload: {
        kind: "agentTurn",
        message,
        deliver: false,
      },
      state: { nextRunAtMs: now },
    };
    const sessionKey = `seatalk:${employeeCode}`;
    const result = await runCronIsolatedAgentTurn({
      cfg,
      deps,
      job,
      message,
      sessionKey,
      lane: "cron",
    });
    const reply =
      (result.outputText && result.outputText.trim()) ||
      (result.summary && result.summary.trim()) ||
      result.error ||
      "处理完成。";
    await sendSingleChat(employeeCode, reply);
  } catch (err) {
    const msg = String(err);
    try {
      await sendSingleChat(employeeCode, `处理出错: ${msg.slice(0, 200)}`);
    } catch {
      // ignore
    }
  }
}
