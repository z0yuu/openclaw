/**
 * SeaTalk 事件回调：URL 校验、签名校验、单聊消息 -> 跑 Agent 并回发 SeaTalk
 * 路径: POST /api/webhook/seatalk
 * 参考: LLM_minecraft app/api/webhook.py
 */

import type { IncomingMessage, ServerResponse } from "node:http";
import { randomUUID } from "node:crypto";
import type { CliDeps } from "../cli/deps.js";
import type { CronJob } from "../cron/types.js";
import { loadConfig } from "../config/config.js";
import { runCronIsolatedAgentTurn } from "../cron/isolated-agent.js";
import { verifySignature, sendSingleChat } from "./client.js";

const SEATALK_WEBHOOK_PATH = "/api/webhook/seatalk";

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
    if (url.pathname !== SEATALK_WEBHOOK_PATH || req.method !== "POST") {
      return false;
    }

    let rawBody: Buffer;
    try {
      rawBody = await readRawBody(req, MAX_BODY_BYTES);
    } catch (err) {
      sendJson(res, 400, { code: 400, message: "Body read error" });
      return true;
    }

    let body: Record<string, unknown>;
    try {
      body = JSON.parse(rawBody.toString("utf8")) as Record<string, unknown>;
    } catch {
      sendJson(res, 400, { code: 400, message: "Invalid JSON" });
      return true;
    }

    const eventType = (body.event_type as string) ?? "";

    // 1. URL 验证
    if (eventType === "event_verification") {
      const event = (body.event as Record<string, unknown>) ?? {};
      const challenge = (event.seatalk_challenge as string) ?? "";
      sendJson(res, 200, { seatalk_challenge: challenge });
      return true;
    }

    // 2. 签名验证
    const signature = (req.headers["signature"] as string) ?? "";
    if (!verifySignature(rawBody, signature)) {
      sendJson(res, 403, { code: 403, message: "Invalid signature" });
      return true;
    }

    // 3. 单聊消息：先快速 200，后台跑 Agent 再回发
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
