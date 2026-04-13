import os
from config.settings import Settings, load_models


def test_settings_reads_telegram_token():
    os.environ["TELEGRAM_BOT_TOKEN"] = "test-token"
    os.environ["MINIMAX_API_KEY"] = "test-key"
    os.environ["DATA_DIR"] = "/tmp/data"
    settings = Settings()
    assert settings.telegram_bot_token == "test-token"
    assert settings.minimax_api_key == "test-key"
    assert settings.data_dir == "/tmp/data"


def test_load_models_default():
    os.environ["MINIMAX_API_KEY"] = "my-key"
    models = load_models()
    assert len(models) >= 1
    assert models[0]["id"] == "minimax-abab65"
    assert models[0]["api_key"] == "my-key"
