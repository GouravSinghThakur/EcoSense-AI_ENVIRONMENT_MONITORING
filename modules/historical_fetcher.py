"""
historical_fetcher.py
─────────────────────
Fetches 90 days of historical weather + air quality data on startup.

Sources:
  Weather    : Open-Meteo API (FREE, no key, hourly, 90-day history)
  Air Quality: OpenWeatherMap /air_pollution/history (free key, hourly, 90 days)

Data is saved as CSVs in data/ keyed by lat/lon so different locations
get their own files. Re-fetch only if the file is older than 24 hours.
"""
from __future__ import annotations

import os
import time
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

DATA_DIR   = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STALE_SECS = 86_400   # 24 hours → re-fetch once per day


def _cache_path(kind: str, lat: float, lon: float) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    tag = f"{lat:.3f}_{lon:.3f}".replace("-", "n")
    return os.path.join(DATA_DIR, f"{kind}_{tag}.csv")


def _is_stale(path: str) -> bool:
    if not os.path.exists(path):
        return True
    age = time.time() - os.path.getmtime(path)
    return age > STALE_SECS


# ── Open-Meteo weather history (no API key) ───────────────────────────────────

def fetch_weather_history(lat: float, lon: float, days: int = 90) -> pd.DataFrame | None:
    path = _cache_path("wx_hist", lat, lon)
    if not _is_stale(path):
        logger.info("Weather history cache fresh — loading from %s", path)
        df = pd.read_csv(path, parse_dates=["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    logger.info("Fetching %d days of weather history from Open-Meteo…", days)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":       lat,
        "longitude":      lon,
        "hourly":         "temperature_2m,relative_humidity_2m,surface_pressure,"
                          "wind_speed_10m,precipitation,cloud_cover,apparent_temperature",
        "wind_speed_unit":"ms",
        "past_days":      days,
        "forecast_days":  1,
        "timezone":       "auto",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hourly = data["hourly"]
        df = pd.DataFrame({
            "timestamp":   pd.to_datetime(hourly["time"]),
            "temperature": hourly["temperature_2m"],
            "feels_like":  hourly["apparent_temperature"],
            "humidity":    hourly["relative_humidity_2m"],
            "pressure":    hourly["surface_pressure"],
            "wind_speed":  hourly["wind_speed_10m"],
            "rain_1h":     hourly["precipitation"],
            "clouds":      hourly["cloud_cover"],
        })
        df.dropna(subset=["temperature"], inplace=True)
        df.set_index("timestamp", inplace=True)
        df.to_csv(path)
        logger.info("Weather history saved: %d rows → %s", len(df), path)
        return df
    except Exception as exc:
        logger.error("Weather history fetch failed: %s", exc)
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df
        return None


# ── OWM Air Pollution history ─────────────────────────────────────────────────

def fetch_aq_history(lat: float, lon: float, api_key: str,
                     days: int = 90) -> pd.DataFrame | None:
    path = _cache_path("aq_hist", lat, lon)
    if not _is_stale(path):
        logger.info("AQ history cache fresh — loading from %s", path)
        df = pd.read_csv(path, parse_dates=["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    if not api_key:
        logger.warning("No API key — cannot fetch AQ history.")
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df
        return None

    logger.info("Fetching %d days of AQ history from OpenWeatherMap…", days)
    from modules.aqi_calculator import calculate_aqi

    end_ts   = int(datetime.now(tz=timezone.utc).timestamp())
    start_ts = int((datetime.now(tz=timezone.utc) - timedelta(days=days)).timestamp())

    url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
    try:
        resp = requests.get(url, params={
            "lat": lat, "lon": lon,
            "start": start_ts, "end": end_ts,
            "appid": api_key,
        }, timeout=60)
        resp.raise_for_status()
        items = resp.json().get("list", [])

        rows = []
        for item in items:
            c = item["components"]
            pollutants = {
                "pm2_5": c.get("pm2_5", 0),
                "pm10":  c.get("pm10",  0),
                "o3":    c.get("o3",    0),
                "co":    c.get("co",    0),
                "so2":   c.get("so2",   0),
                "no2":   c.get("no2",   0),
            }
            aqi_res = calculate_aqi(pollutants)
            rows.append({
                "timestamp": datetime.fromtimestamp(item["dt"]),
                "aqi":       aqi_res["aqi"] if aqi_res else 0,
                "pm2_5":     c.get("pm2_5", 0),
                "pm10":      c.get("pm10",  0),
                "o3":        c.get("o3",    0),
                "co":        c.get("co",    0),
                "so2":       c.get("so2",   0),
                "no2":       c.get("no2",   0),
                "nh3":       c.get("nh3",   0),
            })

        df = pd.DataFrame(rows)
        df.set_index("timestamp", inplace=True)
        df.to_csv(path)
        logger.info("AQ history saved: %d rows → %s", len(df), path)
        return df

    except Exception as exc:
        logger.error("AQ history fetch failed: %s", exc)
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df
        return None


def load_both(lat: float, lon: float, api_key: str = "",
              days: int = 90) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Convenience wrapper — returns (weather_df, aq_df)."""
    wx = fetch_weather_history(lat, lon, days)
    aq = fetch_aq_history(lat, lon, api_key, days)
    return wx, aq
