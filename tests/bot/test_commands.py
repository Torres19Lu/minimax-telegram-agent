from unittest.mock import AsyncMock, MagicMock
import pytest
from telegram import Update
from telegram.ext import ContextTypes
from bot.commands import skill_command, model_command, reset_command


@pytest.mark.asyncio
async def test_reset_command():
    update = MagicMock(spec=Update)
    update.effective_user.id = 42
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {"memory": MagicMock()}

    await reset_command(update, context)
    context.bot_data["memory"].clear_history.assert_called_once_with(42)
    update.message.reply_text.assert_awaited_once()
