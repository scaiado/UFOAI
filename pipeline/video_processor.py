import json
import logging
import subprocess
import tempfile
from pathlib import Path

from config import PROCESSED_DIR, CHUNK_SIZE, CHUNK_OVERLAP, OLLAMA_BASE_URL
from models import ProcessedChunk

logger = logging.getLogger(__name__)


def extract_key_frames(video_path: str, interval: int = 2, max_frames: int = 20) -> list[str]:
    path = Path(video_path)
    if not path.exists():
        logger.warning(f"Video not found: {video_path}")
        return []

    tmp_dir = tempfile.mkdtemp(prefix="ufoai_frames_")
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", str(path),
                "-vf", f"fps=1/{interval},select='eq(scene\\,0.3)'",
                "-frames:v", str(max_frames),
                "-q:v", "2",
                f"{tmp_dir}/frame_%04d.jpg",
            ],
            capture_output=True,
            timeout=300,
        )
    except Exception as e:
        logger.error(f"ffmpeg frame extraction error: {e}")

    frames = sorted(Path(tmp_dir).glob("frame_*.jpg"))
    if not frames:
        logger.info(f"Scene detection found no frames, falling back to uniform sampling for {path.name}")
        try:
            subprocess.run(
                [
                    "ffmpeg", "-i", str(path),
                    "-vf", f"fps=1/{interval}",
                    "-frames:v", str(max_frames),
                    "-q:v", "2",
                    f"{tmp_dir}/frame_%04d.jpg",
                ],
                capture_output=True,
                timeout=300,
            )
            frames = sorted(Path(tmp_dir).glob("frame_*.jpg"))
        except Exception as e:
            logger.error(f"ffmpeg uniform frame extraction error: {e}")

    return [str(f) for f in frames]


def extract_audio(video_path: str) -> str | None:
    path = Path(video_path)
    if not path.exists():
        return None

    audio_path = str(path.with_suffix(".wav"))
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", str(path),
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                "-y", audio_path,
            ],
            capture_output=True,
            timeout=300,
        )
    except Exception as e:
        logger.error(f"Audio extraction error: {e}")
        return None

    return audio_path if Path(audio_path).exists() else None


def transcribe_audio_with_ollama(audio_path: str) -> str:
    import ollama

    path = Path(audio_path)
    if not path.exists():
        return ""

    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        resp = client.generate(
            model="llama3.1:8b",
            prompt=f"Transcribe the following audio file. If you cannot process audio, respond with 'NO_TRANSCRIPTION'. File: {path.name}",
        )
        text = resp.get("response", "")
        if "NO_TRANSCRIPTION" in text:
            return ""
        return text.strip()
    except Exception as e:
        logger.error(f"Ollama transcription error: {e}")
        return ""


def describe_frame_with_vision(image_path: str) -> str:
    import ollama

    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        resp = client.chat(
            model="llava:7b",
            messages=[
                {
                    "role": "user",
                    "content": "Describe this image in detail. Focus on any unusual objects, lights, shapes, movements, or phenomena visible. Note any military equipment, sensors, or instrumentation visible. Be thorough and objective.",
                    "images": [image_path],
                }
            ],
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Vision model error for {image_path}: {e}")
        return ""


def process_video(video_path: str) -> list[ProcessedChunk]:
    path = Path(video_path)
    logger.info(f"Processing video: {path.name}")

    all_text = ""
    chunks = []

    frames = extract_key_frames(video_path)
    if frames:
        all_text += "=== KEY FRAME DESCRIPTIONS ===\n\n"
        for i, frame in enumerate(frames):
            desc = describe_frame_with_vision(frame)
            if desc:
                all_text += f"Frame {i + 1}: {desc}\n\n"

    audio_path = extract_audio(video_path)
    if audio_path:
        transcript = transcribe_audio_with_ollama(audio_path)
        if transcript:
            all_text += f"\n=== AUDIO TRANSCRIPT ===\n\n{transcript}\n"
        Path(audio_path).unlink(missing_ok=True)

    if all_text.strip():
        words = all_text.split()
        start = 0
        idx = 0
        while start < len(words):
            end = start + CHUNK_SIZE
            chunk_words = words[start:end]
            chunks.append(
                ProcessedChunk(
                    source_file=path.name,
                    chunk_index=idx,
                    text=" ".join(chunk_words),
                    chunk_type="video",
                )
            )
            start += CHUNK_SIZE - CHUNK_OVERLAP
            idx += 1

    if chunks:
        out_dir = PROCESSED_DIR / "chunks"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{path.stem}_video.json"
        out_path.write_text(
            json.dumps([c.model_dump() for c in chunks], indent=2, ensure_ascii=False)
        )
        logger.info(f"Processed video {path.name}: {len(chunks)} chunks")

    return chunks
