import json
import os
from telegram import Update
from telegram.ext import ContextTypes

from tools.voice import transcribe_voice


async def _process_user_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_text: str,
) -> None:
    user_id = update.effective_user.id
    memory = context.bot_data["memory"]
    skills = context.bot_data["skills"]
    llm = context.bot_data["llm"]
    tools = context.bot_data["tools"]
    mcp = context.bot_data.get("mcp")

    state = memory.get_state(user_id)
    skill_name = state["current_skill"]
    model_id = state["current_model"]
    history = state["history"]

    skill = skills.get(skill_name)
    system_prompt = skill.system_prompt if skill else "你是一个友善的助手。"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "mcp_web_search",
                "description": "Use MiniMax official MCP to search the internet for current information, weather, news, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        }
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write a file to the sandbox directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Relative path inside sandbox"},
                        "content": {"type": "string", "description": "File content"},
                    },
                    "required": ["filename", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from the sandbox directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Relative path inside sandbox"},
                    },
                    "required": ["filename"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files in the sandbox directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subdir": {"type": "string", "description": "Optional subdirectory inside sandbox"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Execute a Python script in the sandbox and return output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "string", "description": "Python script content"},
                    },
                    "required": ["script"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "execute_shell",
                "description": "Execute a safe shell command in the sandbox and return output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command"},
                    },
                    "required": ["command"],
                },
            },
        },
    ]

    try:
        assistant_message = llm.chat_with_tools(model_id, messages, tool_definitions)
    except Exception as e:
        reply = f"调用模型时出错了: {e}"
        memory.add_message(user_id, "user", user_text)
        memory.add_message(user_id, "assistant", reply)
        await update.message.reply_text(reply)
        return

    if assistant_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_message.tool_calls
            ],
        })

        for tc in assistant_message.tool_calls:
            func_name = tc.function.name
            func_args = json.loads(tc.function.arguments)
            if func_name == "mcp_web_search":
                query = func_args.get("query", "")
                await update.message.reply_text(f"🔍 正在搜索: {query}")
                if mcp:
                    result = await mcp.web_search(query)
                else:
                    # Fallback to local duckduckgo
                    result = tools["web_search"](query)
            elif func_name == "write_file":
                filename = func_args.get("filename", "")
                content = func_args.get("content", "")
                await update.message.reply_text(f"📝 正在写入文件: {filename}")
                result = tools["write_file"](filename, content)
            elif func_name == "read_file":
                filename = func_args.get("filename", "")
                result = tools["read_file"](filename)
            elif func_name == "list_files":
                subdir = func_args.get("subdir", "")
                result = tools["list_files"](subdir)
            elif func_name == "execute_python":
                script = func_args.get("script", "")
                await update.message.reply_text("🐍 正在执行 Python 脚本...")
                result = tools["execute_python"](script)
            elif func_name == "execute_shell":
                command = func_args.get("command", "")
                await update.message.reply_text(f"💻 正在执行命令: {command}")
                result = tools["execute_shell"](command)
            else:
                result = f"未知工具: {func_name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        try:
            reply = llm.chat(model_id, messages)
        except Exception as e:
            reply = f"调用模型时出错了: {e}"
    else:
        reply = assistant_message.content or ""

    memory.add_message(user_id, "user", user_text)
    memory.add_message(user_id, "assistant", reply)
    await update.message.reply_text(reply)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text or ""
    await _process_user_input(update, context, user_text)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.voice
    if not voice:
        await update.message.reply_text("没有收到语音消息。")
        return

    await update.message.reply_text("🎙️ 正在识别语音，请稍等...")

    # Download voice file
    voice_file = await voice.get_file()
    ogg_path = f"/tmp/voice_{update.effective_user.id}_{voice.file_unique_id}.ogg"
    await voice_file.download_to_drive(ogg_path)

    openai_key = context.bot_data.get("openai_api_key", "")
    transcribed = transcribe_voice(ogg_path, openai_key)

    # Clean up downloaded file
    if os.path.exists(ogg_path):
        os.remove(ogg_path)

    if transcribed.startswith("语音转文字") or transcribed.startswith("音频转换") or transcribed.startswith("语音"):
        await update.message.reply_text(f"❌ {transcribed}")
        return

    await update.message.reply_text(f"📝 识别结果: {transcribed}")
    await _process_user_input(update, context, transcribed)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image messages using MiniMax MCP understand_image."""
    mcp = context.bot_data.get("mcp")
    if not mcp:
        await update.message.reply_text("图片理解功能当前不可用（MCP 未连接）。")
        return

    photo = update.message.photo
    if not photo:
        await update.message.reply_text("没有收到图片。")
        return

    # Get highest resolution photo
    largest = photo[-1]
    photo_file = await largest.get_file()
    ext = os.path.splitext(photo_file.file_path)[1] or ".jpg"
    image_path = f"/home/lutorres/interest/minimax-telegram-agent/sandbox/photo_{update.effective_user.id}_{largest.file_unique_id}{ext}"
    await photo_file.download_to_drive(image_path)

    await update.message.reply_text("🖼️ 正在分析图片，请稍等...")

    prompt = update.message.caption or "请描述这张图片的内容。"
    result = await mcp.understand_image(prompt=prompt, image_source=image_path)

    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)

    # Store as a user message with image analysis result
    user_id = update.effective_user.id
    memory = context.bot_data["memory"]
    llm = context.bot_data["llm"]
    skills = context.bot_data["skills"]

    state = memory.get_state(user_id)
    skill_name = state["current_skill"]
    model_id = state["current_model"]
    history = state["history"]

    skill = skills.get(skill_name)
    system_prompt = skill.system_prompt if skill else "你是一个友善的助手。"

    # Build user message combining caption and image analysis
    if update.message.caption:
        combined_user_text = f"[用户发送了一张图片，附言: {update.message.caption}]\n[图片分析结果: {result}]"
    else:
        combined_user_text = f"[用户发送了一张图片]\n[图片分析结果: {result}]"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": combined_user_text})

    try:
        reply = llm.chat(model_id, messages)
    except Exception as e:
        reply = f"调用模型时出错了: {e}"

    memory.add_message(user_id, "user", combined_user_text)
    memory.add_message(user_id, "assistant", reply)
    await update.message.reply_text(reply)
