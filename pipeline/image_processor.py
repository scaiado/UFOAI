import base64
import json
import logging
import os
from pathlib import Path

import pytesseract
from PIL import Image

from config import PROCESSED_DIR, CHUNK_SIZE, CHUNK_OVERLAP, OLLAMA_BASE_URL
from models import ProcessedChunk

logger = logging.getLogger(__name__)

VISION_PROMPT = "Describe this image in detail. Focus on any unusual objects, lights, shapes, movements, or anomalous phenomena visible. Note any military equipment, sensors, instrumentation, or geographical features. Be thorough and objective. This may be a UFO/UAP-related image from government records."


def ocr_image(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR error for {image_path}: {e}")
        return ""


def describe_image_with_vision(image_path: str) -> str:
    use_openrouter = os.environ.get("UFOAI_USE_OPENROUTER") == "1"
    if use_openrouter:
        return _describe_via_openrouter(image_path)
    return _describe_via_ollama(image_path)


def _describe_via_ollama(image_path: str) -> str:
    import ollama

    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        resp = client.chat(
            model="llava:7b",
            messages=[
                {"role": "user", "content": VISION_PROMPT, "images": [image_path]},
            ],
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Ollama vision error for {image_path}: {e}")
        return ""


def _describe_via_openrouter(image_path: str) -> str:
    from openai import OpenAI
    from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
    from rag.openrouter_client import FREE_MODELS

    model_key = os.environ.get("UFOAI_OPENROUTER_MODEL", "")
    model = model_key if model_key else FREE_MODELS.get("gemma", "google/gemma-4-31b-it:free")

    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = Path(image_path).suffix.lower().lstrip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif"}.get(ext, "jpeg")
        data_url = f"data:image/{mime};base64,{b64}"

        client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenRouter vision error for {image_path}: {e}")
        return _describe_via_ollama(image_path)


def process_image(image_path: str) -> list[ProcessedChunk]:
    path = Path(image_path)
    logger.info(f"Processing image: {path.name}")

    all_text = ""

    description = describe_image_with_vision(image_path)
    if description:
        all_text += f"=== IMAGE DESCRIPTION ===\n{description}\n\n"

    ocr_text = ocr_image(image_path)
    if ocr_text:
        all_text += f"=== OCR TEXT ===\n{ocr_text}\n"

    if not all_text.strip():
        logger.warning(f"No text extracted from image {path.name}")
        return []

    words = all_text.split()
    chunks = []
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
                chunk_type="image",
            )
        )
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1

    if chunks:
        out_dir = PROCESSED_DIR / "chunks"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{path.stem}_image.json"
        out_path.write_text(
            json.dumps([c.model_dump() for c in chunks], indent=2, ensure_ascii=False)
        )
        logger.info(f"Processed image {path.name}: {len(chunks)} chunks")

    return chunks
