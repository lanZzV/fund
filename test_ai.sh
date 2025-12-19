#!/bin/bash

# AI分析功能测试脚本

echo "=========================================="
echo "基金市场监控工具 - AI分析功能测试"
echo "=========================================="
echo ""

# 检查环境变量
echo "1. 检查环境变量配置..."
echo ""

if [ -z "$LLM_API_KEY" ]; then
    echo "⚠️  未配置 LLM_API_KEY"
    echo ""
    echo "请先配置API Key："
    echo "export LLM_API_KEY=\"your-api-key\""
    echo ""
    echo "推荐使用DeepSeek（性价比高）："
    echo "export LLM_API_BASE=\"https://api.deepseek.com/v1\""
    echo "export LLM_MODEL=\"deepseek-chat\""
    echo ""
    echo "配置后，程序会自动进行AI分析。"
    echo "如不需要AI分析，可以直接运行程序。"
    echo ""
else
    echo "✅ LLM_API_KEY: 已配置"
    echo "✅ LLM_API_BASE: ${LLM_API_BASE:-https://api.openai.com/v1}"
    echo "✅ LLM_MODEL: ${LLM_MODEL:-gpt-3.5-turbo}"
    echo ""
fi

echo "=========================================="
echo "2. 运行程序..."
echo "=========================================="
echo ""

# 运行程序
python3 fund.py

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
