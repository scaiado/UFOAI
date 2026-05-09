import json
import logging
import tempfile
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from config import PROCESSED_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from models import ProcessedChunk

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, use_ocr: bool = True) -> list[ProcessedChunk]:
    path = Path(pdf_path)
    if not path.exists():
        logger.warning(f"PDF not found: {pdf_path}")
        return []

    chunks = []
    try:
        doc = fitz.open(str(path))
        full_text = ""
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text").strip()

            if text:
                full_text += f"\n--- Page {page_num + 1}/{total_pages} ---\n{text}"
            elif use_ocr:
                ocr_text = _ocr_page(page, page_num, total_pages)
                if ocr_text:
                    full_text += f"\n--- Page {page_num + 1}/{total_pages} (OCR) ---\n{ocr_text}"

        doc.close()

        if not full_text.strip():
            logger.warning(f"No text extracted from {path.name}")
            return []

        chunks = _chunk_text(full_text, path.name, "pdf")
        logger.info(f"Extracted {len(chunks)} chunks from {path.name} ({total_pages} pages)")
    except Exception as e:
        logger.error(f"Error processing PDF {path.name}: {e}")

    return chunks


def _ocr_page(page, page_num: int, total_pages: int) -> str:
    import io

    try:
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        text = pytesseract.image_to_string(img)
        if text.strip():
            logger.debug(f"OCR page {page_num + 1}/{total_pages}: {len(text)} chars")
        return text.strip()
    except Exception as e:
        logger.debug(f"OCR failed for page {page_num + 1}: {e}")
        return ""


def _chunk_text(text: str, source_file: str, chunk_type: str) -> list[ProcessedChunk]:
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    idx = 0
    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append(
            ProcessedChunk(
                source_file=source_file,
                chunk_index=idx,
                text=chunk_text,
                chunk_type=chunk_type,
            )
        )
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1

    return chunks


def save_chunks(chunks: list[ProcessedChunk], output_name: str):
    out_dir = PROCESSED_DIR / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{output_name}.json"
    out_path.write_text(
        json.dumps([c.model_dump() for c in chunks], indent=2, ensure_ascii=False)
    )
