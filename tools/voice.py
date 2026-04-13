import os
import subprocess
from typing import Optional
from openai import OpenAI


def transcribe_voice(file_path: str, api_key: str) -> str:
    """Transcribe a voice file using OpenAI Whisper API."""
    if not api_key:
        return "语音转文字功能未配置（缺少 OPENAI_API_KEY）。"

    # Convert ogg to mp3 for Whisper API
    base, _ = os.path.splitext(file_path)
    mp3_path = f"{base}.mp3"

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", "-b:a", "32k", mp3_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        return f"音频转换失败: {e}"

    client = OpenAI(api_key=api_key)
    try:
        with open(mp3_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return transcript.text
    except Exception as e:
        return f"语音转文字失败: {e}"
    finally:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
