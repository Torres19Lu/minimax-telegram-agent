from unittest.mock import patch, MagicMock
from llm.client import LLMClient


def test_llm_client_chat():
    models = [
        {
            "id": "test-model",
            "name": "Test",
            "provider": "minimax",
            "model": "test-chat",
            "base_url": "https://test.example/v1",
            "api_key": "test-key",
        }
    ]
    client = LLMClient(models)

    with patch("llm.client.OpenAI") as MockOpenAI:
        mock = MagicMock()
        mock.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="hello from test"))
        ]
        MockOpenAI.return_value = mock

        result = client.chat("test-model", [{"role": "user", "content": "hi"}])
        assert result == "hello from test"
        MockOpenAI.assert_called_once_with(base_url="https://test.example/v1", api_key="test-key")
