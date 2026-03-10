
import subprocess
import tempfile
import os
from typing import Tuple

from youtube_transcript_api import YouTubeTranscriptApi
from faster_whisper import WhisperModel


def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    raise ValueError("Invalid YouTube URL")


def get_caption_transcript(video_id: str) -> str:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t["text"] for t in transcript])


def whisper_transcribe(url: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        audio_path = os.path.join(tmp, "audio.m4a")

        subprocess.run(
            ["yt-dlp", "-f", "bestaudio", "-o", audio_path, url],
            check=True,
        )

        model = WhisperModel("base", compute_type="int8")
        segments, _ = model.transcribe(audio_path)

        return " ".join(seg.text for seg in segments)


def youtube_to_text(url: str) -> Tuple[str, str]:
    video_id = extract_video_id(url)

    try:
        text = get_caption_transcript(video_id)
        source = "captions"
    except Exception:
        text = whisper_transcribe(url)
        source = "whisper"

    return text.strip(), source