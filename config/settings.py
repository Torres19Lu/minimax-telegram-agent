import json
import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    minimax_api_key: str
    data_dir: str = "/app/data"
    models_json: str = ""
    default_model: str = "minimax-abab65"
    max_history: int = 20


def load_models(settings: Settings | None = None) -> List[Dict[str, Any]]:
    if settings is None:
        settings = Settings()

    if settings.models_json:
        raw = json.loads(settings.models_json)
    else:
        raw = [
            {
                "id": "minimax-abab65",
                "name": "MiniMax abab6.5",
                "provider": "minimax",
                "model": "abab6.5-chat",
                "base_url": "https://api.minimax.chat/v1",
                "api_key": settings.minimax_api_key,
            },
            {
                "id": "minimax-abab65s",
                "name": "MiniMax abab6.5s",
                "provider": "minimax",
                "model": "abab6.5s-chat",
                "base_url": "https://api.minimax.chat/v1",
                "api_key": settings.minimax_api_key,
            },
        ]

    for m in raw:
        if isinstance(m.get("api_key"), str) and m["api_key"].startswith("${") and m["api_key"].endswith("}"):
            env_var = m["api_key"][2:-1]
            m["api_key"] = os.getenv(env_var, "")
    return raw
