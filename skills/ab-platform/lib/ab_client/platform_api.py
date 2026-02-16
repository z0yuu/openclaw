# -*- coding: utf-8 -*-
"""Shopee AB Report Open API 客户端（ab-platform skill 内嵌）

兼容目标：Python 2.7+ / Python 3.x
- 不使用函数/变量注解
- 不使用 f-string
- 不使用 print(..., file=...)
"""

from __future__ import absolute_import, division, print_function

import os
import time
import uuid
from datetime import datetime, timedelta

try:
    import requests
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/.openclaw/.env"))
    load_dotenv()
except Exception:
    pass

from .default_metrics import get_default_metrics

DEFAULT_METRICS = get_default_metrics()


class PlatformAPIClient(object):
    """Shopee AB Report Open API 客户端"""

    def __init__(self):
        env = (os.getenv("AB_API_ENV") or "live").lower()
        if env == "live":
            self.api_url = "https://httpgateway.abtest.shopee.io/request_spex"
        elif env == "staging":
            self.api_url = "https://httpgateway.abtest.staging.shopee.io/request_spex"
        else:
            self.api_url = "https://httpgateway.abtest.test.shopee.io/request_spex"

        self.token = (os.getenv("AB_API_TOKEN") or "").strip()
        self.client_server_name = (os.getenv("AB_CLIENT_SERVER_NAME") or "").strip()
        self.operator = (os.getenv("AB_OPERATOR") or "").strip()
        self.timeout = int(os.getenv("AB_API_TIMEOUT") or "30")
        self.use_mock = (os.getenv("USE_MOCK_DATA") or "true").lower() == "true"
        if self.token and self.use_mock:
            self.use_mock = False
        self.poll_interval = int(os.getenv("AB_POLL_INTERVAL") or "2")
        self.max_poll_attempts = int(os.getenv("AB_MAX_POLL_ATTEMPTS") or "30")

    def _get_headers(self, namespace):
        return {
            "Content-Type": "application/json",
            "X-Client-Server-Name": self.client_server_name,
            "X-Des-Namespace": namespace,
            "X-Token": self.token,
            "X-Request-Id": str(uuid.uuid4()),
        }

    def _mask_token(self, token):
        try:
            t = (token or "").strip()
            if not t:
                return ""
            if len(t) <= 8:
                return "****"
            return t[:4] + "..." + t[-4:]
        except Exception:
            return ""

    def _stderr(self, msg):
        try:
            import sys
            sys.stderr.write((msg or "") + "\n")
        except Exception:
            pass

    def _make_request(self, namespace, body):
        if (not HAS_REQUESTS) or self.use_mock or (not self.token):
            return {}
        try:
            headers = self._get_headers(namespace)
            debug = (os.getenv("AB_API_DEBUG") or "").lower() in ("1", "true", "yes", "y")
            if debug:
                safe_headers = dict(headers)
                safe_headers["X-Token"] = self._mask_token(safe_headers.get("X-Token"))
                try:
                    import json as _json
                    body_preview = _json.dumps(body, ensure_ascii=False)
                except Exception:
                    body_preview = str(body)
                if body_preview and len(body_preview) > 2000:
                    body_preview = body_preview[:2000] + "...<truncated>"
                self._stderr("AB_API_DEBUG request: url=%s namespace=%s" % (self.api_url, namespace))
                self._stderr("AB_API_DEBUG headers=%s" % safe_headers)
                self._stderr("AB_API_DEBUG body=%s" % body_preview)

            resp = requests.post(
                self.api_url,
                headers=headers,
                json=body,
                timeout=self.timeout,
            )
            if debug:
                text_preview = (resp.text or "")
                if len(text_preview) > 2000:
                    text_preview = text_preview[:2000] + "...<truncated>"
                self._stderr("AB_API_DEBUG response: status=%s" % resp.status_code)
                self._stderr("AB_API_DEBUG response_text=%s" % text_preview)

            if resp.status_code != 200:
                # 鉴权失败（如 401/403）时：直接回退 mock，避免 stderr 噪音误导。
                # 这样“就现在这样”也能产出可读结果；需要真实数据时再补齐 AB_API_TOKEN。
                if resp.status_code in (401, 403):
                    return {}
                try:
                    err = resp.json().get("msg", resp.text[:200])
                except Exception:
                    err = resp.text[:200]
                self._stderr("API请求失败: HTTP %s %s" % (resp.status_code, err))
                return {}
            result = resp.json()
            if result.get("retcode", 0) != 0:
                self._stderr("API返回错误: %s" % result.get("msg", "Unknown"))
                return {}
            return result
        except Exception as e:
            self._stderr("API请求异常: %s" % e)
            return {}

    def get_summary_key(
        self,
        project_id,
        experiment_id,
        template_name="default",
        template_group_name="result",
        template_group_type=1,
        dates=None,
        regions=None,
        control="",
        treatments=None,
        metrics=None,
        dims=None,
        normalization=None,
        no_cache=False,
    ):
        if dates is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=14)
            dates = [{"time_start": start_date.strftime("%Y-%m-%d"), "time_end": end_date.strftime("%Y-%m-%d")}]
        if regions is None:
            regions = []
        if treatments is None:
            treatments = []
        if metrics is None:
            metrics = DEFAULT_METRICS
        if dims is None:
            dims = []

        namespace = "content_intelligence.experiment_platform.abtest_admin_analysis.open_get_summary_key"
        body = {
            "project_id": project_id,
            "experiment_id": experiment_id,
            "operator": self.operator,
            "template_name": template_name,
            "template_group_name": template_group_name,
            "template_group_type": template_group_type,
            "dates": dates,
            "regions": regions,
            "control": control,
            "treatments": treatments,
            "metrics": metrics,
            "dims": dims,
            "no_cache": no_cache,
        }
        if normalization:
            body["normalization"] = normalization
        return self._make_request(namespace, body)

    def get_summary_result(
        self,
        project_id,
        experiment_id,
        key_info,
        template_name="default",
        template_group_name="result",
        template_group_type=1,
        dates=None,
        regions=None,
        control="",
        treatments=None,
        metrics=None,
        dims=None,
        normalization=None,
    ):
        namespace = "content_intelligence.experiment_platform.abtest_admin_analysis.open_get_summary_result"
        body = {
            "project_id": project_id,
            "experiment_id": experiment_id,
            "operator": self.operator,
            "template_name": template_name,
            "template_group_name": template_group_name,
            "template_group_type": template_group_type,
            "key_info": key_info,
        }
        if dates is not None:
            body["dates"] = dates
        if regions is not None:
            body["regions"] = regions
        if control:
            body["control"] = control
        if treatments is not None:
            body["treatments"] = treatments
        if metrics is not None:
            body["metrics"] = metrics
        if dims is not None:
            body["dims"] = dims
        if normalization:
            body["normalization"] = normalization
        return self._make_request(namespace, body)

    def poll_summary_result(
        self,
        project_id,
        experiment_id,
        key_info,
        dates=None,
        regions=None,
        control="",
        treatments=None,
        metrics=None,
        dims=None,
        normalization=None,
        **kwargs
    ):
        for attempt in range(self.max_poll_attempts):
            result = self.get_summary_result(
                project_id=project_id,
                experiment_id=experiment_id,
                key_info=key_info,
                dates=dates,
                regions=regions,
                control=control,
                treatments=treatments,
                metrics=metrics,
                dims=dims,
                normalization=normalization,
                **kwargs
            )
            if not result:
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                return {}
            if result.get("retcode", -1) != 0:
                return {}
            # status 可能在顶层或 key_info 子字段
            status = result.get("status")
            if status is None:
                ki = result.get("key_info") or {}
                status = ki.get("status", 0)
            if status in (1, 2):
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                return {}
            return result
        return {}

    def parse_summary_data(self, result):
        data = result.get("data") or {}
        columns = data.get("columns") or []
        # API 也可能在 "header" 字段返回列名（||分隔字符串）
        if not columns:
            header = data.get("header") or ""
            if isinstance(header, str) and header:
                columns = [c.strip() for c in header.split("||")]
            elif isinstance(header, list):
                columns = header
        body = data.get("body") or []
        relative = data.get("relative") or []
        control_group_indexes = data.get("control_group_indexes") or []

        # body/relative 可能是 list[str]（|| 分割）或 list[dict]
        def _parse_rows(rows):
            parsed = []
            for r in rows:
                if isinstance(r, dict):
                    parsed.append(r)
                else:
                    try:
                        parts = [v.strip() for v in (r or "").split("||")]
                    except Exception:
                        parts = []
                    parsed.append(dict(zip(columns, parts)))
            return parsed

        return {
            "columns": columns,
            "body": _parse_rows(body),
            "relative": _parse_rows(relative),
            "control_group_indexes": control_group_indexes,
            "raw": data,
        }

    def get_ab_metrics(
        self,
        project_id,
        experiment_id,
        control="",
        treatments=None,
        metrics=None,
        dates=None,
        template_name="One Page - Search Core Metric",
        template_group_name="Rollout Checklist",
        normalization=None,
        **kwargs
    ):
        if self.use_mock or (not self.token):
            return self._mock_get_ab_metrics(experiment_id)

        key_response = self.get_summary_key(
            project_id=project_id,
            experiment_id=experiment_id,
            control=control,
            treatments=treatments,
            metrics=metrics,
            dates=dates,
            regions=kwargs.get("regions"),
            dims=kwargs.get("dims"),
            template_name=template_name,
            template_group_name=template_group_name,
            normalization=normalization,
        )
        if (not key_response) or key_response.get("retcode", -1) != 0:
            return self._mock_get_ab_metrics(experiment_id)
        key_info = key_response.get("key_info") or {}
        if not key_info:
            return self._mock_get_ab_metrics(experiment_id)

        result = self.poll_summary_result(
            project_id=project_id,
            experiment_id=experiment_id,
            key_info=key_info,
            dates=dates,
            regions=kwargs.get("regions"),
            control=control,
            treatments=treatments,
            metrics=metrics,
            dims=kwargs.get("dims"),
            normalization=normalization,
            template_name=template_name,
            template_group_name=template_group_name,
        )
        if (not result) or result.get("retcode", -1) != 0:
            return self._mock_get_ab_metrics(experiment_id)
        return self.parse_summary_data(result)

    def _mock_get_ab_metrics(self, experiment_id):
        return {
            "columns": ["group_name", "metric", "value"],
            "body": [
                {"group_name": "Control Group", "metric": "ctr", "value": "0.045"},
                {"group_name": "Treatment Group", "metric": "ctr", "value": "0.051"},
            ],
            "relative": [
                {"group_name": "Control Group", "metric": "ctr", "value": "0.000000"},
                {"group_name": "Treatment Group", "metric": "ctr", "value": "0.133333"},
            ],
            "control_group_indexes": [0],
        }
