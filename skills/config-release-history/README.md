# 需要现在本地搭建opsgw服务

#命令: curl https://proxy.uss.s3.sz.shopee.io/api/v4/50064306/stoc-sg-live/opsgw_caller_agent_install.sh | sh 安装完成后 可以先用我的下述配置即可（小心外传）

export OPSGW_BU="shopee"
export OPSGW_ENV="live"
export OPSGW_APP_ID="search_rankservice_shopee_live"
export OPSGW_APP_SECRET="83yMSdY04j72"

之后启动服务 nohup ./opsgw-caller-agent-linux-amd64 --skip-pid-check &

整体参考 https://confluence.shopee.io/display/STS/%5BOpsAPI+Gateway%5D+Caller+SDK
从 Shopee Config Platform（通过 OpsGW）获取指定 namespace 的历史发布记录，并自动计算相邻版本之间的 diff，以表格/摘要方式展示。
