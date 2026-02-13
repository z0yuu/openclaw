/**
 * SeaTalk Open Platform API 客户端（Node）
 * 参考: https://open.seatalk.io/docs/api-development-guide_
 * 与 LLM_minecraft lib/seatalk/client.py 行为一致：签名算法 SHA256(raw_body + signing_secret)
 */

import { createHash } from "node:crypto";

const OPENAPI_HOST = "https://openapi.seatalk.io";
const API_ACCESS_TOKEN = "/auth/app_access_token";
const API_SINGLE_CHAT = "/messaging/v2/single_chat";
const CODE_OK = 0;
const CODE_TOKEN_EXPIRED = 100;
const MAX_SINGLE_CHAT_BYTES = 4000;

let cachedToken: string | null = null;
let tokenExpireAt = 0;

function getAppId(): string {
  return process.env.SEATALK_APP_ID ?? "";
}

function getAppSecret(): string {
  return process.env.SEATALK_APP_SECRET ?? "";
}

function getSigningSecret(): string {
  return process.env.SEATALK_SIGNING_SECRET ?? "";
}

/**
 * 验证 SeaTalk 回调签名：SHA256(raw_body + signing_secret)
 * 未配置 SEATALK_SIGNING_SECRET 时视为通过。
 */
export function verifySignature(rawBody: Buffer, signature: string): boolean {
  const secret = getSigningSecret();
  if (!secret) {
    return true;
  }
  const payload = Buffer.concat([rawBody, Buffer.from(secret, "utf8")]);
  const calculated = createHash("sha256").update(payload).digest("hex");
  return calculated === signature;
}

async function refreshAccessToken(): Promise<string> {
  const appId = getAppId();
  const appSecret = getAppSecret();
  if (!appId || !appSecret) {
    throw new Error("SEATALK_APP_ID and SEATALK_APP_SECRET are required");
  }
  const res = await fetch(`${OPENAPI_HOST}${API_ACCESS_TOKEN}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_id: appId, app_secret: appSecret }),
  });
  if (!res.ok) {
    throw new Error(`SeaTalk token request failed: ${res.status}`);
  }
  const data = (await res.json()) as { code?: number; app_access_token?: string; expire?: number };
  if (data.code !== CODE_OK) {
    throw new Error(`SeaTalk token error: ${JSON.stringify(data)}`);
  }
  const token = data.app_access_token;
  if (!token) {
    throw new Error("SeaTalk token response missing app_access_token");
  }
  cachedToken = token;
  tokenExpireAt = Date.now() + (data.expire ?? 7200) * 1000 - 10000;
  return token;
}

export async function getAccessToken(): Promise<string> {
  if (cachedToken && Date.now() < tokenExpireAt) {
    return cachedToken;
  }
  return refreshAccessToken();
}

/**
 * 发送单聊消息。内容超过约 4000 字节时会分段发送（每段带 [i/n] 前缀）。
 */
export async function sendSingleChat(
  employeeCode: string,
  content: string,
  _contentType: "text" | "markdown" = "text",
): Promise<void> {
  const token = await getAccessToken();
  const encoded = Buffer.from(content, "utf8");
  if (encoded.length <= MAX_SINGLE_CHAT_BYTES) {
    await sendSingleChatOne(employeeCode, content, token);
    return;
  }
  const chunks = splitTextByBytes(content, MAX_SINGLE_CHAT_BYTES);
  for (let i = 0; i < chunks.length; i++) {
    const part = chunks.length > 1 ? `[${i + 1}/${chunks.length}]\n${chunks[i]}` : chunks[i];
    await sendSingleChatOne(employeeCode, part, token);
  }
}

async function sendSingleChatOne(
  employeeCode: string,
  content: string,
  token: string,
): Promise<void> {
  const body = {
    employee_code: employeeCode,
    message: { tag: "text", text: { content } },
  };
  const res = await fetch(`${OPENAPI_HOST}${API_SINGLE_CHAT}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`SeaTalk send failed: ${res.status} ${text}`);
  }
  const data = (await res.json()) as { code?: number };
  if (data.code === CODE_TOKEN_EXPIRED) {
    await refreshAccessToken();
    await sendSingleChatOne(employeeCode, content, (await getAccessToken()) as string);
    return;
  }
  if (data.code !== CODE_OK) {
    throw new Error(`SeaTalk API error: ${JSON.stringify(data)}`);
  }
}

function splitTextByBytes(text: string, maxBytes: number): string[] {
  const chunks: string[] = [];
  const lines = text.split("\n");
  let current = "";
  for (const line of lines) {
    const next = current ? current + "\n" + line : line;
    if (Buffer.byteLength(next, "utf8") > maxBytes) {
      if (current) {
        chunks.push(current);
      }
      current = line;
    } else {
      current = next;
    }
  }
  if (current) {
    chunks.push(current);
  }
  return chunks.length ? chunks : [text.slice(0, 1000)];
}
