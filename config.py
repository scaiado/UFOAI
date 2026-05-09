import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = Path(os.getenv("RAW_DATA_DIR", str(DATA_DIR / "raw")))
PROCESSED_DIR = Path(os.getenv("PROCESSED_DATA_DIR", str(DATA_DIR / "processed")))
EMBEDDINGS_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "embeddings")))
MANIFEST_PATH = DATA_DIR / "manifest.json"

WAR_GOV_BASE = "https://www.war.gov"
WAR_GOV_UFO_CSV = f"{WAR_GOV_BASE}/Portals/1/Interactive/2026/UFO/uap-csv.csv"
WAR_GOV_SLIDESHOW_DIR = f"{WAR_GOV_BASE}/portals/1/Interactive/2026/UFO/Slideshow"
DVIDS_API_BASE = "https://api.dvidshub.net/asset"
DVIDS_API_KEY = "key-68bb60d16b35e"

AARO_BASE = "https://www.aaro.mil"
AARO_SECTIONS = [
    f"{AARO_BASE}/UAP-Cases/Official-UAP-Imagery/",
    f"{AARO_BASE}/UAP-Records/",
    f"{AARO_BASE}/EFOIA-Reading-Room/",
    f"{AARO_BASE}/Congressional-Press-Products/",
]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
OPENROUTER_REASONING_MODEL = os.getenv("OPENROUTER_REASONING_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free")

CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1:8b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
VISION_MODEL = os.getenv("VISION_MODEL", "llava:7b")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RECORDS_PER_PAGE = 10

SLIDESHOW_IMAGES = [
    "FBI-Photo-1.jpg",
    "FBI-Photo-A5.jpg",
    "FBI-Photo-B2.jpg",
    "FBI-Photo-B7-.jpg",
    "FBI-Photo-B18.jpg",
    "FBI-Photo-B20.jpg",
    "2024-04-30-Composite-Sketch.jpg",
    "NASA-UAP-VM6-Apollo-17-1972.jpg",
    "DOW-UAP-PR19-Unresolved-UAP-Report-Middle-East-May-2022.jpg",
    "DOW-UAP-PR26-Unresolved-UAP-Report-United-Arab-Emirates-October-2023.jpg",
    "DOW-UAP-PR34-Unresolved-UAP-Report-Greece-October-2023.jpg",
    "DOW-UAP-PR35-Unresolved-UAP-Report-Greece-October-2023.jpg",
    "DOW-UAP-PR38-Unresolved-UAP-Report-Middle-East-2013.jpg",
    "DOW-UAP-PR43-Unresolved-UAP-Report-Africa-2025.jpg",
    "DOW-UAP-PR45-Unresolved-UAP-Report-Middle-East-2020.jpg",
    "DOW-UAP-PR46-Unresolved-UAP-Report-INDOPACOM-2024.jpg",
    "DOW-UAP-PR49-Unresolved-UAP-Report-Department-of-the-Army-2026.jpg",
]

for d in [RAW_DIR, PROCESSED_DIR, EMBEDDINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
