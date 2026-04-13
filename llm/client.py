from typing import List, Dict, Any
from openai import OpenAI


class LLMClient:
    def __init__(self, models: List[Dict[str, Any]]):
        self.models = {m["id"]: m for m in models}

    def _client(self, model_id: str):
        if model_id not in self.models:
            raise ValueError(f"Unknown model: {model_id}")
        cfg = self.models[model_id]
        return OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"]), cfg["model"]

    def chat(self, model_id: str, messages: List[Dict[str, str]]) -> str:
        client, model = self._client(model_id)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    def chat_with_tools(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Any:
        client, model = self._client(model_id)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        return response.choices[0].message
