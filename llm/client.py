from typing import List, Dict, Any
from openai import OpenAI


class LLMClient:
    def __init__(self, models: List[Dict[str, Any]]):
        self.models = {m["id"]: m for m in models}

    def chat(self, model_id: str, messages: List[Dict[str, str]]) -> str:
        if model_id not in self.models:
            raise ValueError(f"Unknown model: {model_id}")
        cfg = self.models[model_id]
        client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
        response = client.chat.completions.create(
            model=cfg["model"],
            messages=messages,
        )
        return response.choices[0].message.content or ""
