import csv
import json
import io
import logging
from pathlib import Path

from curl_cffi import requests as cffi_requests

from config import (
    WAR_GOV_UFO_CSV,
    WAR_GOV_SLIDESHOW_DIR,
    DVIDS_API_BASE,
    DVIDS_API_KEY,
    RAW_DIR,
    MANIFEST_PATH,
    SLIDESHOW_IMAGES,
)
from models import UAPRecord

logger = logging.getLogger(__name__)

_IMPERSONATE = "chrome131"


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"records": {}, "slideshow": [], "last_scrape": None}


def save_manifest(manifest: dict):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def _download_file(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = cffi_requests.get(url, impersonate=_IMPERSONATE, timeout=120, allow_redirects=True)
        if resp.status_code != 200:
            logger.warning(f"Failed to download {url}: {resp.status_code}")
            return False
        dest.write_bytes(resp.content)
        logger.info(f"Downloaded {dest.name}")
        return True
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False


def _resolve_video_url(video_id: str) -> list[str]:
    urls = []
    try:
        resp = cffi_requests.get(
            DVIDS_API_BASE,
            params={"api_key": DVIDS_API_KEY, "id": f"video:{video_id}", "thumb_width": 720},
            impersonate=_IMPERSONATE,
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            files = data.get("results", {}).get("files", [])
            for f in files:
                if f.get("type") == "video" and f.get("format") == "mp4":
                    urls.append(f["url"])
            urls.sort(key=lambda u: u.count("high") or u.count("720") or 0, reverse=True)
    except Exception as e:
        logger.error(f"Error resolving video {video_id}: {e}")
    return urls


def parse_csv(csv_text: str) -> list[UAPRecord]:
    records = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        title = (row.get("Title") or "").strip()
        if not title:
            continue

        doc_url = (row.get("PDF | Image Link") or "").strip()
        modal_raw = (row.get("Modal Image") or "").strip()
        modal_images = [u.strip() for u in modal_raw.split("|") if u.strip()] if modal_raw else []
        dvids_raw = (row.get("DVIDS Video ID") or "").strip()
        dvids_ids = [v.strip() for v in dvids_raw.split("|") if v.strip()] if dvids_raw else []

        file_type = (row.get("Type") or "").strip().upper()
        if dvids_ids and not file_type:
            file_type = "VID"
        elif doc_url and not file_type:
            ext = Path(doc_url).suffix.lower()
            file_type = "VID" if ext in (".mp4", ".webm", ".mov") else "PDF" if ext == ".pdf" else "IMG"

        records.append(
            UAPRecord(
                title=title,
                file_type=file_type,
                description=(row.get("Description Blurb") or "").strip(),
                agency=(row.get("Agency") or "").strip(),
                incident_date=(row.get("Incident Date") or "").strip(),
                incident_location=(row.get("Incident Location") or "").strip(),
                release_date=(row.get("Release Date") or "").strip(),
                document_url=doc_url or None,
                thumbnail_url=modal_images[0] if modal_images else None,
                modal_images=modal_images,
                dvids_video_ids=dvids_ids,
                video_pairing=(row.get("Video Pairing") or "").strip() or None,
                pdf_pairing=(row.get("PDF Pairing") or "").strip() or None,
                video_title=(row.get("Video Title") or "").strip() or None,
                redacted=(row.get("Redaction") or "").strip().upper() == "TRUE",
                source="war.gov",
            )
        )
    return records


def _fetch_csv() -> str:
    logger.info("Fetching UAP CSV from war.gov...")
    resp = cffi_requests.get(WAR_GOV_UFO_CSV, impersonate=_IMPERSONATE, timeout=60, allow_redirects=True)
    resp.raise_for_status()

    csv_path = RAW_DIR / "uap-csv.csv"
    csv_path.write_text(resp.text)
    logger.info(f"CSV saved: {len(resp.text)} chars")
    return resp.text


def scrape_war_gov(force: bool = False) -> list[UAPRecord]:
    manifest = load_manifest()

    csv_path = RAW_DIR / "uap-csv.csv"
    if csv_path.exists() and not force:
        csv_text = csv_path.read_text()
        logger.info(f"Using cached CSV ({len(csv_text)} chars)")
    else:
        csv_text = _fetch_csv()

    records = parse_csv(csv_text)
    logger.info(f"Parsed {len(records)} records from CSV")

    new_downloads = 0
    for rec in records:
        safe_name = rec.title.replace("/", "_").replace("\\", "_").replace(" ", "_")[:120]
        rec_key = f"{rec.source}:{safe_name}"

        if manifest["records"].get(rec_key, {}).get("downloaded") and not force:
            rec.local_path = manifest["records"][rec_key].get("local_path")
            rec.video_urls = manifest["records"][rec_key].get("video_urls", [])
            continue

        if rec.document_url:
            ext = Path(rec.document_url).suffix or ".bin"
            local = RAW_DIR / "documents" / f"{safe_name}{ext}"
            if _download_file(rec.document_url, local):
                rec.local_path = str(local)
                new_downloads += 1

        if rec.dvids_video_ids:
            video_urls = []
            for vid_id in rec.dvids_video_ids:
                urls = _resolve_video_url(vid_id)
                video_urls.extend(urls)
                for vurl in urls[:1]:
                    local = RAW_DIR / "videos" / f"{safe_name}_{vid_id}.mp4"
                    _download_file(vurl, local)
            rec.video_urls = video_urls

        for idx, img_url in enumerate(rec.modal_images):
            if img_url:
                ext = Path(img_url).suffix or ".jpg"
                _download_file(img_url, RAW_DIR / "images" / f"{safe_name}_modal_{idx}{ext}")

        manifest["records"][rec_key] = {
            "title": rec.title,
            "downloaded": True,
            "local_path": rec.local_path,
            "video_urls": rec.video_urls,
        }

    for img_name in SLIDESHOW_IMAGES:
        if img_name not in manifest["slideshow"] or force:
            url = f"{WAR_GOV_SLIDESHOW_DIR}/{img_name}"
            local = RAW_DIR / "slideshow" / img_name
            if _download_file(url, local):
                manifest["slideshow"].append(img_name)

    from datetime import datetime

    manifest["last_scrape"] = datetime.now().isoformat()
    save_manifest(manifest)
    logger.info(f"Scrape complete. {new_downloads} new files downloaded.")
    return records
