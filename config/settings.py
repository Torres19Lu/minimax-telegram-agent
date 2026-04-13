import json
import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    minimax_api_key: str
    openai_api_key: str = ""
    data_dir: str = "/app/data"
    models_json: str = ""
    default_model: str = "minimax-m27"
    max_history: int = 20


def load_models(settings: Settings | None = None) -> List[Dict[str, Any]]:
    if settings is None:
        settings = Settings()

    if settings.models_json:
        raw = json.loads(settings.models_json)
    else:
        raw = [
            {
                "id": "minimax-m27",
                "name": "MiniMax M2.7",
                "provider": "minimax",
                "model": "MiniMax-M2.7",
                "base_url": "https://api.minimaxi.com/v1",
                "api_key": settings.minimax_api_key,
            },
            {
                "id": "minimax-m27-highspeed",
                "name": "MiniMax M2.7 极速版",
                "provider": "minimax",
                "model": "MiniMax-M2.7-highspeed",
                "base_url": "https://api.minimaxi.com/v1",
                "api_key": settings.minimax_api_key,
            },
        ]

    for m in raw:
        if isinstance(m.get("api_key"), str) and m["api_key"].startswith("${") and m["api_key"].endswith("}"):
            env_var = m["api_key"][2:-1]
            m["api_key"] = os.getenv(env_var, "")
    return raw
