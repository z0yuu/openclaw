"""
默认指标配置（AB 平台 skill 内嵌）
"""

DEFAULT_METRICS = [
    "order_cnt",
    "gmv",
    "gmv_995",
    "gmv_995_v2",
    "nmv",
    "ads_load",
    "ads_revenue_usd",
    "bad_query_rate",
]

METRICS_DESCRIPTION = {
    "order_cnt": "订单数",
    "gmv": "GMV (成交金额)",
    "gmv_995": "GMV 995",
    "gmv_995_v2": "GMV 995 v2",
    "nmv": "NMV (净成交金额)",
    "ads_load": "广告加载率 (paidads)",
    "ads_revenue_usd": "广告收入 (USD)",
    "bad_query_rate": "坏查询率 (org+ads)",
}


def get_default_metrics():
    return list(DEFAULT_METRICS)


def get_metrics_description(metric: str) -> str:
    return METRICS_DESCRIPTION.get(metric, metric)
