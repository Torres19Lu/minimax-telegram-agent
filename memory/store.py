import json
import os
from typing import Dict, Any


class MemoryStore:
    def __init__(self, data_dir: str, default_skill: str = "default", default_model: str = "minimax-abab65", max_history: int = 20):
        self.data_dir = data_dir
        self.default_skill = default_skill
        self.default_model = default_model
        self.max_history = max_history
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, user_id: int) -> str:
        return os.path.join(self.data_dir, f"{user_id}.json")

    def get_state(self, user_id: int) -> Dict[str, Any]:
        path = self._path(user_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "current_skill": self.default_skill,
            "current_model": self.default_model,
            "history": [],
        }

    def _save(self, user_id: int, state: Dict[str, Any]) -> None:
        with open(self._path(user_id), "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def add_message(self, user_id: int, role: str, content: str) -> None:
        state = self.get_state(user_id)
        state["history"].append({"role": role, "content": content})
        if len(state["history"]) > self.max_history * 2:
            state["history"] = state["history"][-(self.max_history * 2):]
        self._save(user_id, state)

    def set_skill(self, user_id: int, skill_name: str) -> None:
        state = self.get_state(user_id)
        state["current_skill"] = skill_name
        self._save(user_id, state)

    def set_model(self, user_id: int, model_id: str) -> None:
        state = self.get_state(user_id)
        state["current_model"] = model_id
        self._save(user_id, state)

    def clear_history(self, user_id: int) -> None:
        state = self.get_state(user_id)
        state["history"] = []
        self._save(user_id, state)
