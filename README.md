# MiniMax Telegram Agent

一个基于 MiniMax API 的多功能 Telegram 机器人，支持文字、语音、图片交互，具备联网搜索、图片理解、沙盒代码执行和可切换的 Skill 人格系统。

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **文字对话** | 基于 MiniMax 大模型（OpenAI 兼容接口）的自然语言对话 |
| **语音消息** | 本地 `faster-whisper` 语音转文字，无需额外付费 API |
| **图片理解** | 通过 MiniMax 官方 MCP `understand_image` 分析图片内容 |
| **联网搜索** | 优先调用 MiniMax MCP `web_search`，不可用时自动回退到 DuckDuckGo / Tavily |
| **代码执行** | 在 `sandbox/` 目录内安全执行 Python 脚本和 Shell 命令 |
| **文件操作** | 在沙盒内读写文件、浏览目录结构 |
| **Skill 人格** | 通过 Markdown 文件定义不同角色（通用助手、编程专家、文案写手等），支持热切换 |
| **模型切换** | 支持在 MiniMax M2.7 和 M2.7 极速版之间切换 |
| **持久记忆** | 每个用户独立的 JSON 对话历史，自动维护最近 N 轮上下文 |

---

## 项目结构

```
minimax-telegram-agent/
├── bot/                  # Telegram 消息处理器和命令
│   ├── commands.py       # /skill /model /reset 命令
│   └── handlers.py       # 文字、语音、图片消息处理
├── config/               # 配置管理
│   └── settings.py       # 环境变量、模型列表加载
├── llm/                  # LLM 客户端
│   └── client.py         # OpenAI 兼容接口封装
├── memory/               # 用户对话记忆
│   └── store.py          # 基于 JSON 文件的持久化存储
├── skills/               # Skill 人格定义（Markdown + YAML frontmatter）
│   ├── default.md
│   ├── coder.md
│   └── writer.md
├── tools/                # 工具集
│   ├── search.py         # DuckDuckGo / Tavily 搜索
│   ├── voice.py          # faster-whisper 本地语音转文字
│   └── code_executor.py  # 沙盒文件与代码执行
├── mcp_client/           # MiniMax MCP 客户端
│   └── wrapper.py        # stdio 连接 web_search / understand_image
├── tests/                # pytest 测试套件
├── scripts/              # 启动与部署脚本
│   ├── start.sh          # 本地启动脚本（加载 .env、SOCKS5 代理）
│   └── deploy.sh         # fly.io 一键部署脚本
├── main.py               # 应用入口
├── Dockerfile
├── fly.toml
└── requirements.txt
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Torres19Lu/minimax-telegram-agent.git
cd minimax-telegram-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> **注意**：语音转文字依赖 `ffmpeg`，请确保系统已安装。

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
MINIMAX_API_KEY=your-minimax-api-key
DATA_DIR=./data
# 可选：Tavily API key，用于搜索回退
TAVILY_API_KEY=your-tavily-api-key
# 可选：OpenAI API key（当前仅作为备用，语音已使用本地模型）
OPENAI_API_KEY=your-openai-api-key
```

### 4. 本地启动

```bash
bash scripts/start.sh
```

`start.sh` 会自动加载 `.env`、检查必要变量，并设置 SOCKS5 代理（默认 `socks5://127.0.0.1:10808`）。

---

## Telegram 命令

| 命令 | 说明 |
|------|------|
| `/skill` | 查看当前 Skill 和可用列表 |
| `/skill <name>` | 切换到指定 Skill |
| `/model` | 查看当前模型和可用列表 |
| `/model <id>` | 切换到指定模型 |
| `/reset` | 清空当前用户的对话历史 |

---

## Skill 系统

Skill 是定义 Agent 人格的 Markdown 文件，位于 `skills/` 目录。文件格式如下：

```markdown
---
name: coder
description: 编程专家
---

你是一个经验丰富的全栈工程师，擅长 Python、JavaScript 和系统设计。
回答问题时请给出清晰的代码示例和最佳实践建议。
```

- `name`：Skill 的唯一标识
- `description`：在 `/skill` 命令中显示的简介
- 正文：作为系统提示词（`system_prompt`）注入对话

新增 Skill 只需在 `skills/` 下创建新的 `.md` 文件，重启 Bot 即可生效。

---

## 部署到 fly.io

项目已内置 `fly.toml` 和 `deploy.sh`，支持一键部署：

```bash
bash scripts/deploy.sh
```

脚本会自动完成：
1. 检查并安装 `flyctl`
2. 创建应用（如不存在）
3. 创建持久化 Volume（`hermes_data`，挂载到 `/app/data`）
4. 提示输入 Secrets 并设置
5. 执行 `flyctl deploy`

---

## 技术栈

- **框架**：`python-telegram-bot` v20+（异步架构）
- **大模型**：MiniMax（OpenAI 兼容接口）
- **MCP**：`minimax-coding-plan-mcp`（官方 Token Plan MCP）
- **语音**：`faster-whisper`（tiny 模型，CPU int8）
- **搜索**：DuckDuckGo（主回退）/ Tavily（次回退）
- **配置**：`pydantic-settings` + `.env`
- **测试**：`pytest` + `pytest-asyncio`
- **部署**：Docker + fly.io

---

## 网络代理

如果你的运行环境无法直接访问 Telegram 或 HuggingFace，可以在 `.env` 或启动前设置代理：

```bash
export ALL_PROXY=socks5://127.0.0.1:10808
```

`scripts/start.sh` 已默认配置该代理。

---

## 沙盒安全

代码执行和文件操作被严格限制在 `sandbox/` 目录内：
- 所有路径经过 `_validate_path` 校验，禁止目录穿越
- Python 脚本和 Shell 命令均有 30 秒超时
- Shell 命令黑名单拦截明显危险的指令（如 `rm -rf /`）

---

## 测试

```bash
PYTHONPATH=. pytest -v
```

---

## 许可证

MIT License
