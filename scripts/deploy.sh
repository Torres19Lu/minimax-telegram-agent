#!/usr/bin/env bash
set -e

APP_NAME="minimax-telegram-agent"

echo "==> Deploying ${APP_NAME} to fly.io..."

# Ensure flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "flyctl not found. Installing..."
    curl -L https://fly.io/install.sh | sh
fi

# Login if needed
flyctl auth whoami &> /dev/null || flyctl auth login

# Create app if not exists
if ! flyctl apps list | grep -q "${APP_NAME}"; then
    echo "==> Creating app..."
    flyctl apps create "${APP_NAME}"
fi

# Create volume if not exists
if ! flyctl volumes list --app "${APP_NAME}" | grep -q "hermes_data"; then
    echo "==> Creating persistent volume..."
    flyctl volumes create hermes_data --size 1 --region sin --app "${APP_NAME}"
fi

# Prompt for secrets
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    read -sp "Enter TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
    echo
fi

if [ -z "$MINIMAX_API_KEY" ]; then
    read -sp "Enter MINIMAX_API_KEY: " MINIMAX_API_KEY
    echo
fi

echo "==> Setting secrets..."
flyctl secrets set TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}" MINIMAX_API_KEY="${MINIMAX_API_KEY}" --app "${APP_NAME}"

echo "==> Deploying..."
flyctl deploy --app "${APP_NAME}"

echo "==> Done!"
