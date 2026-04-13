import os
import subprocess
from typing import Optional


def transcribe_voice(file_path: str, api_key: str = "") -> str:
    """Transcribe a voice file using local faster-whisper model."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "语音转文字功能未配置（缺少 faster-whisper 依赖）。"

    # Convert ogg to wav for faster-whisper
    base, _ = os.path.splitext(file_path)
    wav_path = f"{base}.wav"

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        return f"音频转换失败: {e}"

    try:
        # Use tiny model for fast inference and low memory usage
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(wav_path, beam_size=5, language="zh")
        text = "".join([segment.text for segment in segments]).strip()
        if not text:
            return "未能识别到语音内容，请尝试更清晰地说普通话。"
        return text
    except Exception as e:
        return f"语音转文字失败: {e}"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
