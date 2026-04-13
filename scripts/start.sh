#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 加载 .env 文件中的环境变量
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
    echo "==> 已加载环境变量: ${PROJECT_ROOT}/.env"
else
    echo "==> 警告: 未找到 ${PROJECT_ROOT}/.env 文件"
fi

# 检查必要的环境变量
if [ -z "${TELEGRAM_BOT_TOKEN}" ]; then
    echo "==> 错误: TELEGRAM_BOT_TOKEN 未设置"
    exit 1
fi

if [ -z "${MINIMAX_API_KEY}" ]; then
    echo "==> 错误: MINIMAX_API_KEY 未设置"
    exit 1
fi

# 设置默认数据目录
export DATA_DIR="${DATA_DIR:-${PROJECT_ROOT}/data}"

# 设置 SOCKS5 代理（根据你的 V2RayN 配置）
export ALL_PROXY="${ALL_PROXY:-socks5://127.0.0.1:10808}"

echo "==> 启动 MiniMax Telegram Agent..."
echo "==> 数据目录: ${DATA_DIR}"
echo "==> 代理: ${ALL_PROXY}"

cd "${PROJECT_ROOT}"
python main.py
