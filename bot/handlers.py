import json
from telegram import Update
from telegram.ext import ContextTypes


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text or ""

    memory = context.bot_data["memory"]
    skills = context.bot_data["skills"]
    llm = context.bot_data["llm"]
    tools = context.bot_data["tools"]

    state = memory.get_state(user_id)
    skill_name = state["current_skill"]
    model_id = state["current_model"]
    history = state["history"]

    skill = skills.get(skill_name)
    system_prompt = skill.system_prompt if skill else "你是一个友善的助手。"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    # Define available tools for the LLM
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the internet for current information, weather, news, etc.",
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
        }
    ]

    try:
        assistant_message = llm.chat_with_tools(model_id, messages, tool_definitions)
    except Exception as e:
        reply = f"调用模型时出错了: {e}"
        memory.add_message(user_id, "user", user_text)
        memory.add_message(user_id, "assistant", reply)
        await update.message.reply_text(reply)
        return

    # Handle tool calls
    if assistant_message.tool_calls:
        # Add assistant message with tool_calls to conversation
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
            if func_name == "web_search":
                query = func_args.get("query", "")
                await update.message.reply_text(f"🔍 正在搜索: {query}")
                result = tools["web_search"](query)
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
