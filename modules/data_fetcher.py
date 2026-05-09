"""
data_fetcher.py
---------------
Handles all external API calls to OpenWeatherMap.
Includes retry logic, timeouts, and structured error handling.
"""
import os
import logging
import yaml
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", ".env"))
_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
with open(_config_path, "r") as _f:
    config = yaml.safe_load(_f)

WEATHER_ENDPOINT     = config["api"]["weather_endpoint"]
AIR_QUALITY_ENDPOINT = config["api"]["air_quality_endpoint"]
FORECAST_ENDPOINT    = config["api"]["forecast_endpoint"]
UNITS                = config["api"]["units"]
REQUEST_TIMEOUT      = config["api"].get("timeout_seconds", 10)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_api_key() -> str:
    key = os.getenv("OPENWEATHERMAP_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "OPENWEATHERMAP_API_KEY is not set. "
            "Add it to config/.env or as a Hugging Face Space secret."
        )
    return key


def _safe_get(url: str, params: dict) -> dict | None:
    """Single HTTP GET with a timeout; raises on HTTP errors."""
    params["appid"] = _get_api_key()
    resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ── Public API ────────────────────────────────────────────────────────────────

@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=False,
)
def fetch_current_weather(lat: float, lon: float) -> dict | None:
    """Fetch current weather conditions for given coordinates."""
    try:
        return _safe_get(WEATHER_ENDPOINT, {"lat": lat, "lon": lon, "units": UNITS})
    except EnvironmentError as e:
        logger.error(str(e))
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Weather fetch failed: %s", e)
        raise  # let tenacity retry


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=False,
)
def fetch_air_quality(lat: float, lon: float) -> dict | None:
    """Fetch current air quality for given coordinates."""
    try:
        return _safe_get(AIR_QUALITY_ENDPOINT, {"lat": lat, "lon": lon})
    except EnvironmentError as e:
        logger.error(str(e))
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Air-quality fetch failed: %s", e)
        raise


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=False,
)
def fetch_weather_forecast(lat: float, lon: float, cnt: int = 40) -> dict | None:
    """Fetch 5-day / 3-hour weather forecast."""
    try:
        return _safe_get(FORECAST_ENDPOINT, {"lat": lat, "lon": lon, "units": UNITS, "cnt": cnt})
    except EnvironmentError as e:
        logger.error(str(e))
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Forecast fetch failed: %s", e)
        raise


def get_location_by_name(city_name: str) -> tuple[float, float] | None:
    """Geocode a city name to (lat, lon). Returns None on failure."""
    try:
        data = _safe_get(
            "http://api.openweathermap.org/geo/1.0/direct",
            {"q": city_name, "limit": 1},
        )
        if data:
            return data[0]["lat"], data[0]["lon"]
        logger.warning("No geocode result for: %s", city_name)
        return None
    except Exception as e:
        logger.error("Geocoding failed for '%s': %s", city_name, e)
        return None