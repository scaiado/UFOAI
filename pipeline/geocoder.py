import json
import logging
from pathlib import Path

from config import PROCESSED_DIR, OPENROUTER_API_KEY, OPENROUTER_BASE_URL

logger = logging.getLogger(__name__)

CACHE_PATH = PROCESSED_DIR / "geocoded_locations.json"

LOCATIONS = [
    "Western United States", "Arabian Gulf", "Syria", "Iraq", "Moon",
    "United States", "Mediterranean Sea", "Middle East", "Greece",
    "Low Earth Orbit", "Germany", "Gulf of Oman", "Aegean Sea",
    "Arabian Sea", "Gulf of Aden", "Strait of Hormuz",
    "United Arab Emirates", "Netherlands", "Azerbaijan", "Detroit, MI",
    "Pacific Time Zone", "Pacific Ocean", "Iran", "Djibouti",
    "Southern United States", "East China Sea", "Japan", "Indo-PACOM",
    "North America", "Papua New Guinea", "Kazakhstan", "Georgia",
    "Turkmenistan", "Mexico", "Arabian Sea", "Africa",
]

DEFAULT_GEOCODES = {
    "Western United States": (39.8283, -98.5795),
    "Arabian Gulf": (26.0, 51.0),
    "Syria": (35.0, 38.0),
    "Iraq": (33.0, 44.0),
    "Moon": (0.0, 0.0),
    "United States": (39.8283, -98.5795),
    "Mediterranean Sea": (35.0, 18.0),
    "Middle East": (30.0, 45.0),
    "Greece": (39.0, 22.0),
    "Low Earth Orbit": (0.0, 0.0),
    "Germany": (51.0, 10.0),
    "Gulf of Oman": (24.0, 59.0),
    "Aegean Sea": (38.5, 25.0),
    "Arabian Sea": (15.0, 65.0),
    "Gulf of Aden": (12.5, 45.0),
    "Strait of Hormuz": (26.5, 56.5),
    "United Arab Emirates": (24.0, 54.0),
    "Netherlands": (52.1, 5.3),
    "Azerbaijan": (40.1, 47.5),
    "Detroit, MI": (42.3314, -83.0458),
    "Pacific Time Zone": (37.0, -122.0),
    "Pacific Ocean": (0.0, -160.0),
    "Iran": (32.4279, 53.6880),
    "Djibouti": (11.8251, 42.5903),
    "Southern United States": (33.0, -90.0),
    "East China Sea": (29.0, 126.0),
    "Japan": (36.2, 138.3),
    "Indo-PACOM": (20.0, 135.0),
    "North America": (45.0, -100.0),
    "Papua New Guinea": (-6.3, 143.9),
    "Kazakhstan": (48.0, 68.0),
    "Georgia": (42.3, 43.4),
    "Turkmenistan": (39.0, 59.0),
    "Mexico": (23.6, -102.5),
    "Africa": (5.0, 22.0),
}


def geocode_all(force: bool = False) -> dict:
    if CACHE_PATH.exists() and not force:
        return json.loads(CACHE_PATH.read_text())

    geocodes = dict(DEFAULT_GEOCODES)

    if OPENROUTER_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
            missing = [loc for loc in LOCATIONS if loc not in geocodes]
            if missing:
                prompt = (
                    "Return ONLY a JSON object mapping each location name to [latitude, longitude]. "
                    "Use approximate coordinates for vague regions. No explanation.\n\n"
                    + "\n".join(f"- {loc}" for loc in missing)
                )
                resp = client.chat.completions.create(
                    model="google/gemma-4-31b-it:free",
                    messages=[{"role": "user", "content": prompt}],
                )
                text = resp.choices[0].message.content.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0]
                parsed = json.loads(text)
                for loc, coords in parsed.items():
                    if isinstance(coords, list) and len(coords) == 2:
                        geocodes[loc] = tuple(coords)
        except Exception as e:
            logger.warning(f"LLM geocoding fallback to defaults: {e}")

    CACHE_PATH.write_text(json.dumps(geocodes, indent=2))
    logger.info(f"Geocoded {len(geocodes)} locations")
    return geocodes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    geocode_all(force=True)
