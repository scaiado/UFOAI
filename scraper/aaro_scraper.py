import logging
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from config import AARO_SECTIONS, RAW_DIR
from models import UAPRecord

logger = logging.getLogger(__name__)


def _download_file(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=120) as resp:
            if resp.status_code != 200:
                return False
            with open(dest, "wb") as f:
                for chunk in resp.iter_bytes(8192):
                    f.write(chunk)
        logger.info(f"Downloaded {dest.name}")
        return True
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False


def _extract_pdf_links(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            title = a.get_text(strip=True) or Path(href).stem
            links.append({"url": href, "title": title})
    return links


def _extract_image_links(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if any(src.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif")):
            if not src.startswith("http"):
                src = base_url.rstrip("/") + "/" + src.lstrip("/")
            alt = img.get("alt", "") or Path(src).stem
            links.append({"url": src, "title": alt})
    return links


def scrape_aaro() -> list[UAPRecord]:
    records = []
    for section_url in AARO_SECTIONS:
        try:
            logger.info(f"Scraping {section_url}")
            resp = httpx.get(section_url, follow_redirects=True, timeout=30)
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch {section_url}: {resp.status_code}")
                continue

            pdf_links = _extract_pdf_links(resp.text, section_url)
            img_links = _extract_image_links(resp.text, section_url)

            for link in pdf_links:
                safe_name = re.sub(r"[^\w\-]", "_", link["title"])[:120]
                local = RAW_DIR / "aaro" / "documents" / f"{safe_name}.pdf"
                _download_file(link["url"], local)
                records.append(
                    UAPRecord(
                        title=link["title"],
                        file_type="PDF",
                        description="",
                        agency="AARO",
                        incident_date="N/A",
                        incident_location="N/A",
                        release_date="N/A",
                        document_url=link["url"],
                        source="aaro.mil",
                        local_path=str(local) if local.exists() else None,
                    )
                )

            for link in img_links:
                safe_name = re.sub(r"[^\w\-]", "_", link["title"])[:120]
                ext = Path(link["url"]).suffix or ".jpg"
                local = RAW_DIR / "aaro" / "images" / f"{safe_name}{ext}"
                _download_file(link["url"], local)
                records.append(
                    UAPRecord(
                        title=link["title"],
                        file_type="IMG",
                        description="",
                        agency="AARO",
                        incident_date="N/A",
                        incident_location="N/A",
                        release_date="N/A",
                        document_url=link["url"],
                        source="aaro.mil",
                        local_path=str(local) if local.exists() else None,
                    )
                )

            logger.info(f"Found {len(pdf_links)} PDFs, {len(img_links)} images from {section_url}")
        except Exception as e:
            logger.error(f"Error scraping {section_url}: {e}")

    return records
