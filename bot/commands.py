from telegram import Update
from telegram.ext import ContextTypes


async def skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    memory = context.bot_data["memory"]
    skills = context.bot_data["skills"]
    user_id = update.effective_user.id
    args = context.args

    if not args:
        current = memory.get_state(user_id)["current_skill"]
        lines = [f"当前 Skill: `{current}`", "\n可用 Skill:"]
        for name, skill in skills.items():
            lines.append(f"- `{name}`: {skill.description}")
        lines.append("\n切换命令: `/skill <name>`")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    skill_name = args[0].strip()
    if skill_name not in skills:
        await update.message.reply_text(f"未知的 Skill: `{skill_name}`", parse_mode="Markdown")
        return

    memory.set_skill(user_id, skill_name)
    await update.message.reply_text(f"已切换到 Skill: `{skill_name}`", parse_mode="Markdown")


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    memory = context.bot_data["memory"]
    models = context.bot_data["models"]
    user_id = update.effective_user.id
    args = context.args

    if not args:
        current = memory.get_state(user_id)["current_model"]
        lines = [f"当前模型: `{current}`", "\n可用模型:"]
        for m in models:
            lines.append(f"- `{m['id']}`: {m['name']}")
        lines.append("\n切换命令: `/model <id>`")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    model_id = args[0].strip()
    ids = {m["id"] for m in models}
    if model_id not in ids:
        await update.message.reply_text(f"未知的模型: `{model_id}`", parse_mode="Markdown")
        return

    memory.set_model(user_id, model_id)
    await update.message.reply_text(f"已切换到模型: `{model_id}`", parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    context.bot_data["memory"].clear_history(user_id)
    await update.message.reply_text("对话历史已清空。")
