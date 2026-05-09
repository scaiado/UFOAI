import logging
import time

from scraper.war_gov_scraper import scrape_war_gov
from scraper.aaro_scraper import scrape_aaro

logger = logging.getLogger(__name__)


def scrape_all(force: bool = False):
    logger.info("Starting full scrape...")
    records = []

    try:
        records.extend(scrape_war_gov(force=force))
    except Exception as e:
        logger.error(f"war.gov scrape failed: {e}")

    try:
        records.extend(scrape_aaro())
    except Exception as e:
        logger.error(f"AARO scrape failed: {e}")

    logger.info(f"Total records collected: {len(records)}")
    return records


def scrape_loop(interval_hours: int = 24):
    while True:
        try:
            scrape_all()
        except Exception as e:
            logger.error(f"Scrape loop error: {e}")
        logger.info(f"Sleeping {interval_hours}h until next scrape...")
        time.sleep(interval_hours * 3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    records = scrape_all()
    print(f"Collected {len(records)} records")
