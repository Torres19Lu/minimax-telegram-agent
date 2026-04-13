import os
import tempfile
import json
from memory.store import MemoryStore


def test_memory_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(data_dir=tmpdir, max_history=3)
        state = store.get_state(123)
        assert state["current_skill"] == "default"
        assert state["current_model"] == "minimax-abab65"
        assert state["history"] == []

        store.add_message(123, "user", "hello")
        store.add_message(123, "assistant", "hi")
        state = store.get_state(123)
        assert len(state["history"]) == 2

        store.set_skill(123, "coder")
        store.set_model(123, "minimax-abab65s")
        state = store.get_state(123)
        assert state["current_skill"] == "coder"
        assert state["current_model"] == "minimax-abab65s"

        store.clear_history(123)
        state = store.get_state(123)
        assert state["history"] == []
