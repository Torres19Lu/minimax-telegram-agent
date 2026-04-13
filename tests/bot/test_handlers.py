from unittest.mock import AsyncMock, MagicMock
import pytest
from telegram import Update
from telegram.ext import ContextTypes
from bot.handlers import message_handler


@pytest.mark.asyncio
async def test_message_handler_without_tools():
    update = MagicMock(spec=Update)
    update.effective_user.id = 42
    update.message = MagicMock()
    update.message.text = "hello"
    update.message.reply_text = AsyncMock()

    memory = MagicMock()
    memory.get_state.return_value = {
        "current_skill": "default",
        "current_model": "test-model",
        "history": [],
    }

    skills = {"default": MagicMock(system_prompt="you are helpful")}
    llm_client = MagicMock()
    assistant_msg = MagicMock()
    assistant_msg.content = "hi there"
    assistant_msg.tool_calls = None
    llm_client.chat_with_tools.return_value = assistant_msg

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {"memory": memory, "skills": skills, "llm": llm_client, "tools": {}}

    await message_handler(update, context)
    update.message.reply_text.assert_awaited_once_with("hi there")
    memory.add_message.assert_any_call(42, "user", "hello")
    memory.add_message.assert_any_call(42, "assistant", "hi there")
