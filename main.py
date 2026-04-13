import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config.settings import Settings, load_models
from skills.loader import load_skills
from memory.store import MemoryStore
from llm.client import LLMClient
from bot.commands import skill_command, model_command, reset_command
from bot.handlers import message_handler, voice_handler
from tools.search import web_search

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    settings = Settings()
    os.makedirs(settings.data_dir, exist_ok=True)

    skills = load_skills(os.path.join(os.path.dirname(__file__), "skills"))
    models = load_models(settings)
    memory = MemoryStore(
        data_dir=settings.data_dir,
        default_skill="default",
        default_model=settings.default_model,
        max_history=settings.max_history,
    )
    llm = LLMClient(models)
    tools = {
        "web_search": web_search,
    }

    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.bot_data["skills"] = skills
    application.bot_data["models"] = models
    application.bot_data["memory"] = memory
    application.bot_data["llm"] = llm
    application.bot_data["tools"] = tools
    application.bot_data["openai_api_key"] = settings.openai_api_key

    application.add_handler(CommandHandler("skill", skill_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
