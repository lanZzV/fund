#!/bin/bash

# 加载.env文件中的环境变量
if [ -f .env ]; then
    echo "正在加载 .env 配置文件..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 环境变量已加载"
    echo "   - LLM_API_BASE: $LLM_API_BASE"
    echo "   - LLM_MODEL: $LLM_MODEL"
    echo "   - LLM_API_KEY: ${LLM_API_KEY:0:15}..."
    echo ""
else
    echo "⚠️  未找到 .env 文件"
    exit 1
fi

# 运行程序
echo "正在启动基金监控工具..."
echo "=========================================="

# 支持传递命令行参数，包括 --report-dir
# 用法示例：
#   ./run.sh                              # 使用默认报告目录 reports
#   ./run.sh --report-dir /tmp/reports    # 使用自定义报告目录
python3 fund.py "$@"
