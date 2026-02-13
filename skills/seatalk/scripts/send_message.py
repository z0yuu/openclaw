#!/usr/bin/env python3
"""
SeaTalk 消息发送脚本（OpenClaw skill）
通过 SeaTalk Open Platform 发送单聊或群聊消息。
环境变量: SEATALK_APP_ID, SEATALK_APP_SECRET
参考: https://open.seatalk.io/docs
"""

import os
import sys
import time
import argparse
from threading import Lock

try:
    import requests
except ImportError:
    print("需要安装 requests: pip install requests", file=sys.stderr)
    sys.exit(1)

OPENAPI_HOST = "https://openapi.seatalk.io"
API_ACCESS_TOKEN = "/auth/app_access_token"
API_SINGLE_CHAT = "/messaging/v2/single_chat"
API_GROUP_CHAT = "/messaging/v2/group_chat"
CODE_OK = 0
CODE_TOKEN_EXPIRED = 100


class SeaTalkClient:
    """SeaTalk Open Platform 客户端（精简版）"""

    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = (app_id or os.getenv("SEATALK_APP_ID", "")).strip()
        self.app_secret = (app_secret or os.getenv("SEATALK_APP_SECRET", "")).strip()
        self._access_token = ""
        self._token_expire = 0
        self._lock = Lock()

    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_secret)

    def _refresh_access_token(self) -> None:
        resp = requests.post(
            f"{OPENAPI_HOST}{API_ACCESS_TOKEN}",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code", -1) != CODE_OK:
            raise ValueError(f"获取 access_token 失败: {data}")
        self._access_token = data["app_access_token"]
        self._token_expire = int(time.time()) + data.get("expire", 7200)

    def get_access_token(self) -> str:
        if not self._access_token or self._token_expire - int(time.time()) < 10:
            with self._lock:
                if not self._access_token or self._token_expire - int(time.time()) < 10:
                    self._refresh_access_token()
        return self._access_token

    def _request(self, method: str, path: str, json_data: dict, retry: bool = True) -> dict:
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        resp = requests.request(method, f"{OPENAPI_HOST}{path}", json=json_data, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == CODE_OK:
            return data
        if data.get("code") == CODE_TOKEN_EXPIRED and retry:
            self._refresh_access_token()
            return self._request(method, path, json_data, retry=False)
        raise ValueError(f"SeaTalk API 错误: {data}")

    @staticmethod
    def _message(content: str, content_type: str = "text") -> dict:
        if content_type not in ("text", "markdown"):
            content_type = "text"
        return {"tag": content_type, content_type: {"content": content}}

    def send_single(self, employee_code: str, content: str, content_type: str = "text") -> dict:
        return self._request("post", API_SINGLE_CHAT, {
            "employee_code": employee_code.strip(),
            "message": self._message(content, content_type),
        })

    def send_group(
        self,
        group_code: str,
        content: str,
        content_type: str = "text",
        mentioned_emails: list = None,
        at_all: bool = False,
    ) -> dict:
        payload = {
            "group_code": group_code.strip(),
            "message": self._message(content, content_type),
        }
        if mentioned_emails:
            payload["mentioned_emails"] = [e.strip() for e in mentioned_emails]
        if at_all:
            payload["at_all"] = True
        return self._request("post", API_GROUP_CHAT, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="SeaTalk 发送单聊/群聊消息")
    parser.add_argument("mode", choices=["single", "group"], help="single=单聊, group=群聊")
    parser.add_argument("target", help="单聊为 employee_code，群聊为 group_code")
    parser.add_argument("content", nargs="+", help="消息内容（空格会拼接成一段）")
    parser.add_argument("--markdown", action="store_true", help="以 Markdown 类型发送")
    parser.add_argument("--at-all", action="store_true", help="群聊时 @所有人")
    parser.add_argument("--mention", type=str, default="", help="群聊时 @ 的邮箱，逗号分隔")
    args = parser.parse_args()

    content = " ".join(args.content)
    content_type = "markdown" if args.markdown else "text"

    client = SeaTalkClient()
    if not client.is_configured():
        print("未配置 SEATALK_APP_ID 或 SEATALK_APP_SECRET", file=sys.stderr)
        return 1

    try:
        if args.mode == "single":
            client.send_single(args.target, content, content_type)
            print("已发送单聊消息")
        else:
            mentioned = [e.strip() for e in args.mention.split(",") if e.strip()] or None
            client.send_group(args.target, content, content_type, mentioned_emails=mentioned, at_all=args.at_all)
            print("已发送群聊消息")
        return 0
    except Exception as e:
        print(f"发送失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
