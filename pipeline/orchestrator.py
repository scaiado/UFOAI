import json
import logging
from pathlib import Path

from config import RAW_DIR, PROCESSED_DIR
from models import UAPRecord
from pipeline.pdf_processor import extract_text_from_pdf
from pipeline.video_processor import process_video
from pipeline.image_processor import process_image

logger = logging.getLogger(__name__)


def find_files_to_process() -> dict[str, list[str]]:
    result = {"pdfs": [], "videos": [], "images": []}

    for p in RAW_DIR.rglob("*.pdf"):
        result["pdfs"].append(str(p))

    for ext in ("*.mp4", "*.webm", "*.mov", "*.avi"):
        for p in RAW_DIR.rglob(ext):
            result["videos"].append(str(p))

    for ext in ("*.jpg", "*.jpeg", "*.png", "*.gif"):
        for p in RAW_DIR.rglob(ext):
            thumb = str(p)
            if "/thumbnail/" not in thumb and "/thumbnails/" not in thumb:
                result["images"].append(str(p))

    return result


def get_processed_files() -> set[str]:
    processed = set()
    chunks_dir = PROCESSED_DIR / "chunks"
    if chunks_dir.exists():
        for p in chunks_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text())
                if data:
                    processed.add(data[0].get("source_file", ""))
            except Exception:
                pass
    return processed


def _save_combined(all_chunks):
    combined_path = PROCESSED_DIR / "all_chunks.json"
    existing = []
    if combined_path.exists():
        existing = json.loads(combined_path.read_text())
    existing.extend([c.model_dump() for c in all_chunks])
    combined_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    return len(existing)


def process_all(
    records: list[UAPRecord] | None = None,
    force: bool = False,
    pdfs: bool = True,
    images: bool = True,
    videos: bool = True,
):
    files = find_files_to_process()
    already_processed = get_processed_files() if not force else set()

    all_chunks = []
    total_pdf = len(files["pdfs"])
    total_img = len(files["images"])

    if pdfs:
        for i, pdf_path in enumerate(files["pdfs"]):
            name = Path(pdf_path).name
            if name in already_processed:
                continue
            logger.info(f"[PDF {i+1}/{total_pdf}] {name}")
            chunks = extract_text_from_pdf(pdf_path)
            all_chunks.extend(chunks)
            if all_chunks and len(all_chunks) % 50 == 0:
                _save_combined(all_chunks)
                all_chunks = []

    if videos:
        for video_path in files["videos"]:
            name = Path(video_path).name
            if name in already_processed:
                continue
            chunks = process_video(video_path)
            all_chunks.extend(chunks)

    if images:
        for i, image_path in enumerate(files["images"]):
            name = Path(image_path).name
            if name in already_processed:
                continue
            logger.info(f"[IMG {i+1}/{total_img}] {name}")
            chunks = process_image(image_path)
            all_chunks.extend(chunks)

    if records:
        for rec in records:
            if rec.description:
                from models import ProcessedChunk

                all_chunks.append(
                    ProcessedChunk(
                        source_file=rec.title,
                        chunk_index=0,
                        text=rec.description,
                        chunk_type="metadata",
                        agency=rec.agency,
                        incident_date=rec.incident_date,
                        incident_location=rec.incident_location,
                        title=rec.title,
                        description=rec.description,
                    )
                )

    total = _save_combined(all_chunks)
    logger.info(f"Processing complete. {len(all_chunks)} new chunks. Total: {total}")
    return all_chunks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_all()
