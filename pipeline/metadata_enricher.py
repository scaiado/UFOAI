import json
import logging
from pathlib import Path

from thefuzz import fuzz

from config import PROCESSED_DIR, RAW_DIR

logger = logging.getLogger(__name__)


def load_csv_records() -> list[dict]:
    csv_path = RAW_DIR / "uap-csv.csv"
    if not csv_path.exists():
        return []

    from scraper.war_gov_scraper import parse_csv
    return [{"title": r.title, "agency": r.agency, "incident_date": r.incident_date,
             "incident_location": r.incident_location, "description": r.description,
             "file_type": r.file_type, "source": r.source} for r in parse_csv(csv_path.read_text())]


def enrich_chunks():
    chunks_path = PROCESSED_DIR / "all_chunks.json"
    if not chunks_path.exists():
        logger.error("No chunks file found")
        return 0

    data = json.loads(chunks_path.read_text())
    records = load_csv_records()
    if not records:
        logger.error("No CSV records to match against")
        return 0

    record_titles = [(r, r["title"].strip().lower()) for r in records]

    enriched = 0
    for chunk in data:
        if chunk.get("agency"):
            continue

        source = chunk.get("source_file", "").strip().lower()
        if not source:
            continue

        clean = source.replace(".pdf", "").replace(".jpg", "").replace(".png", "").replace("_modal_0", "").replace("_image", "")
        clean = clean.replace("_", " ").strip()

        best_score = 0
        best_record = None
        for rec, title in record_titles:
            score = fuzz.token_sort_ratio(clean, title)
            if score > best_score:
                best_score = score
                best_record = rec

        if best_record and best_score >= 60:
            chunk["agency"] = best_record["agency"]
            chunk["incident_date"] = best_record["incident_date"]
            chunk["incident_location"] = best_record["incident_location"]
            chunk["title"] = best_record["title"]
            chunk["description"] = best_record.get("description", "")
            enriched += 1

    chunks_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info(f"Enriched {enriched}/{len(data)} chunks with metadata (threshold=60)")
    return enriched


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    enrich_chunks()
