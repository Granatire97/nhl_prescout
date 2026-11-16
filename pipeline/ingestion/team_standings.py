from datetime import date
import logging
import requests
from pipeline.endpoints import BASE_URL, STANDINGS_ENDPOINT


logger = logging.getLogger(__name__)

def fetch_all_teams() -> dict | None:
    today = date.today()
    standings_url = BASE_URL + STANDINGS_ENDPOINT.format(date=today)
    try:
        response = requests.get(standings_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"ERROR: API request failed: {e}")
        raise