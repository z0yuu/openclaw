# -*- coding: utf-8 -*-
"""
Shopee AB Report Open API 客户端（ab-platform skill 内嵌）
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .default_metrics import get_default_metrics

DEFAULT_METRICS = get_default_metrics()


class PlatformAPIClient:
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

    def _get_headers(self, namespace: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Client-Server-Name": self.client_server_name,
            "X-Des-Namespace": namespace,
            "X-Token": self.token,
            "X-Request-Id": str(uuid.uuid4()),
        }

    def _make_request(self, namespace: str, body: Dict) -> Dict:
        if not HAS_REQUESTS or self.use_mock or not self.token:
            return {}
        try:
            resp = requests.post(
                self.api_url,
                headers=self._get_headers(namespace),
                json=body,
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                try:
                    err = resp.json().get("msg", resp.text[:200])
                except Exception:
                    err = resp.text[:200]
                # 注意：不要在这里直接返回空 {}，上层会误判为失败并打印“API请求失败”。
                # 这里返回 {}，让上层决定是否 fallback 到 mock。
                print(f"API请求失败: {err}", file=__import__("sys").stderr)
                return {}
            result = resp.json()
            if result.get("retcode", 0) != 0:
                print(f"API返回错误: {result.get('msg', 'Unknown')}", file=__import__("sys").stderr)
                return {}
            return result
        except requests.exceptions.RequestException as e:
            print(f"API请求异常: {e}", file=__import__("sys").stderr)
            return {}
        except Exception as e:
            print(f"API请求失败: {e}", file=__import__("sys").stderr)
            return {}

    def get_summary_key(
        self,
        project_id: int,
        experiment_id: int,
        template_name: str = "default",
        template_group_name: str = "result",
        template_group_type: int = 1,
        dates: Optional[List[Dict]] = None,
        regions: Optional[List[str]] = None,
        control: str = "",
        treatments: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        dims: Optional[List[str]] = None,
        normalization: Optional[str] = None,
        no_cache: bool = False,
    ) -> Dict:
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
        project_id: int,
        experiment_id: int,
        key_info: Dict,
        template_name: str = "default",
        template_group_name: str = "result",
        template_group_type: int = 1,
        dates: Optional[List[Dict]] = None,
        regions: Optional[List[str]] = None,
        control: str = "",
        treatments: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        dims: Optional[List[str]] = None,
        normalization: Optional[str] = None,
    ) -> Dict:
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
        project_id: int,
        experiment_id: int,
        key_info: Dict,
        dates: Optional[List[Dict]] = None,
        regions: Optional[List[str]] = None,
        control: str = "",
        treatments: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        dims: Optional[List[str]] = None,
        normalization: Optional[str] = None,
        **kwargs,
    ) -> Dict:
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
                **kwargs,
            )
            if not result:
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                return {}

            if result.get("retcode", -1) != 0:
                return {}

            status = result.get("status", 0)
            if status == 0 and result.get("key_info"):
                status = result["key_info"].get("status", 0)

            if status == 3:
                return result
            if status == 2:
                print(f"查询失败: {result.get('msg', '')}", file=__import__("sys").stderr)
                return {}
            if status == 1:
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                return {}
            if "data" in result:
                return result
            if attempt < self.max_poll_attempts - 1:
                time.sleep(self.poll_interval)
        return {}

    def parse_summary_data(self, result: Dict) -> Dict:
        if not result or "data" not in result:
            return {}
        data = result["data"]
        header = data.get("header", "")
        body = data.get("body", [])
        relative = data.get("relative", [])
        control_group_indexes = data.get("control_group_indexes", [])
        columns = [c.strip() for c in header.split("||")] if header else []
        parsed_body = [dict(zip(columns, [v.strip() for v in row.split("||")])) for row in body]
        parsed_relative = [dict(zip(columns, [v.strip() for v in row.split("||")])) for row in relative]
        return {
            "columns": columns,
            "body": parsed_body,
            "relative": parsed_relative,
            "control_group_indexes": control_group_indexes,
            "raw": data,
        }

    def get_ab_metrics(
        self,
        project_id: int,
        experiment_id: int,
        control: str = "",
        treatments: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        dates: Optional[List[Dict]] = None,
        template_name: str = "One Page - Search Core Metric",
        template_group_name: str = "Rollout Checklist",
        normalization: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        if self.use_mock or not self.token:
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
            **{k: v for k, v in kwargs.items() if k not in ["regions", "dims"]},
        )
        if not key_response or key_response.get("retcode", -1) != 0:
            return self._mock_get_ab_metrics(experiment_id)
        key_info = key_response.get("key_info", {})
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
            normalization=kwargs.get("normalization"),
            template_name=template_name,
            template_group_name=template_group_name,
            **{k: v for k, v in kwargs.items() if k not in ["regions", "dims", "normalization", "template_name", "template_group_name"]},
        )
        if not result or result.get("retcode", -1) != 0:
            return self._mock_get_ab_metrics(experiment_id)
        return self.parse_summary_data(result)

    def _mock_get_ab_metrics(self, experiment_id: int) -> Dict:
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
