from telegram import Update
from telegram.ext import ContextTypes


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text or ""

    memory = context.bot_data["memory"]
    skills = context.bot_data["skills"]
    llm = context.bot_data["llm"]

    state = memory.get_state(user_id)
    skill_name = state["current_skill"]
    model_id = state["current_model"]
    history = state["history"]

    skill = skills.get(skill_name)
    system_prompt = skill.system_prompt if skill else "你是一个友善的助手。"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    try:
        reply = llm.chat(model_id, messages)
    except Exception as e:
        reply = f"调用模型时出错了: {e}"

    memory.add_message(user_id, "user", user_text)
    memory.add_message(user_id, "assistant", reply)
    await update.message.reply_text(reply)
