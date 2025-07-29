#!/bin/bash

# Jarvis AI助手启动脚本

echo "🤖 启动 Jarvis AI助手..."
echo "================================"

# 检查conda环境
if [[ "$CONDA_DEFAULT_ENV" != "qwen" ]]; then
    echo "⚠️  当前不在qwen环境中，尝试激活..."
    source conda activate qwen
fi

# 检查依赖
if ! python -c "import qwen_agent" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ 缺少.env配置文件，请创建.env文件并配置API信息"
    exit 1
fi

echo "🚀 启动Jarvis..."
python jarvis.py 