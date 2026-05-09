"""
realtime_engine.py
──────────────────
Real-time AI prediction + dynamic alert scoring.
Every call generates fresh predictions driven by actual live sensor data,
so values change with each API pull.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from modules.utils import get_aqi_description


# ── Dynamic risk scoring ──────────────────────────────────────────────────────

def compute_risk_scores(weather: dict, aq: dict, weather_history_df: pd.DataFrame | None) -> dict:
    """
    Derive real-time risk probabilities from live sensor values.
    Returns a dict {risk_name: float 0-1} that changes with each reading.
    """
    scores = {}

    temp      = weather.get("temperature",  20.0)
    humidity  = weather.get("humidity",     50.0)
    wind      = weather.get("wind_speed",    3.0)
    rain      = weather.get("rain_1h",       0.0)
    pressure  = weather.get("pressure",   1013.0)
    aqi       = aq.get("aqi",               50)
    pm25      = aq.get("pm2_5",             12.0)
    pm10      = aq.get("pm10",              25.0)
    co        = aq.get("co",                 0.4)

    # --- Flood risk ---
    flood = 0.0
    flood += min(rain / 15.0, 0.5)           # heavy rain ↑
    flood += min(humidity / 200.0, 0.25)     # high humidity ↑
    flood += max(0, (1010 - pressure) / 50)  # low pressure → storm ↑
    if weather_history_df is not None and "rain_1h" in weather_history_df.columns:
        acc_rain = weather_history_df["rain_1h"].tail(6).sum()
        flood += min(acc_rain / 30.0, 0.25)  # accumulated rain ↑
    scores["Flood"] = round(min(flood, 1.0), 3)

    # --- Storm risk ---
    storm = 0.0
    storm += min(wind / 25.0, 0.5)
    storm += max(0, (1013 - pressure) / 30) * 0.3
    storm += min(rain / 10.0, 0.2)
    scores["Storm"] = round(min(storm, 1.0), 3)

    # --- Heatwave risk ---
    heat = 0.0
    heat += max(0, (temp - 28) / 15)        # rises above 28 °C
    heat += max(0, (humidity - 60) / 80) * 0.2
    if weather_history_df is not None and "temperature" in weather_history_df.columns:
        avg6h = weather_history_df["temperature"].tail(6).mean()
        heat += max(0, (avg6h - 30) / 10) * 0.3
    scores["Heatwave"] = round(min(heat, 1.0), 3)

    # --- Air pollution risk ---
    pollution = 0.0
    pollution += min(aqi / 300.0, 0.5)
    pollution += min(pm25 / 75.0, 0.3)
    pollution += min(pm10 / 150.0, 0.15)
    pollution += min(co / 10.0, 0.05)
    scores["Air Pollution"] = round(min(pollution, 1.0), 3)

    return scores


# ── Dynamic temperature forecast ─────────────────────────────────────────────

def predict_temperature(weather: dict, weather_history_df: pd.DataFrame | None,
                        hours: int = 48) -> pd.DataFrame:
    """
    Physics-informed temperature forecast that uses real current conditions.
    Returns DataFrame with columns: predicted, upper, lower.
    """
    now       = datetime.now()
    base_temp = weather.get("temperature", 25.0)
    humidity  = weather.get("humidity",    60.0)
    clouds    = weather.get("clouds",      30.0)

    # Estimate diurnal amplitude from humidity + clouds
    amplitude = max(2.0, 8.0 - humidity * 0.04 - clouds * 0.03)

    # Trend from history
    trend = 0.0
    if weather_history_df is not None and len(weather_history_df) >= 3:
        recent = weather_history_df["temperature"].dropna().tail(6)
        if len(recent) >= 2:
            trend = (recent.iloc[-1] - recent.iloc[0]) / len(recent) * 0.5

    future = pd.date_range(start=now, periods=hours, freq="h")
    hour_of_day = np.array([t.hour for t in future])
    day_offset  = np.arange(hours) / 24.0

    # Sinusoidal daily cycle, peak at 14:00
    cycle       = amplitude * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
    noise       = np.random.normal(0, 0.3, hours)
    predicted   = base_temp + cycle + trend * day_offset + noise

    uncertainty = 1.0 + day_offset * 0.5   # grows further out
    return pd.DataFrame({
        "predicted": predicted,
        "upper":     predicted + uncertainty,
        "lower":     predicted - uncertainty,
    }, index=future)


# ── Dynamic alert generation ─────────────────────────────────────────────────

def generate_dynamic_alerts(weather: dict, aq: dict, risk_scores: dict) -> list[dict]:
    """
    Generate alerts directly from live values — always reflects current state.
    """
    alerts = []
    ts     = datetime.now().strftime("%H:%M:%S")

    temp     = weather.get("temperature", 20.0)
    humidity = weather.get("humidity",    50.0)
    wind     = weather.get("wind_speed",   3.0)
    rain     = weather.get("rain_1h",      0.0)
    pressure = weather.get("pressure",  1013.0)
    aqi      = aq.get("aqi",              50)
    pm25     = aq.get("pm2_5",            12.0)
    co       = aq.get("co",               0.4)

    # Temperature
    if temp >= 40:
        alerts.append({"level":"danger",  "type":"🌡 Extreme Heat",    "msg": f"Temperature {temp:.1f}°C — extreme heatwave conditions.", "ts": ts})
    elif temp >= 35:
        alerts.append({"level":"warning", "type":"🌡 High Temperature","msg": f"Temperature {temp:.1f}°C exceeds safe threshold (35°C).", "ts": ts})
    elif temp <= 0:
        alerts.append({"level":"warning", "type":"🧊 Freezing",        "msg": f"Temperature {temp:.1f}°C — frost conditions.", "ts": ts})

    # Humidity
    if humidity >= 90:
        alerts.append({"level":"warning", "type":"💧 High Humidity",   "msg": f"Humidity {humidity:.0f}% — very uncomfortable, mold risk.", "ts": ts})
    elif humidity <= 20:
        alerts.append({"level":"warning", "type":"🏜 Low Humidity",    "msg": f"Humidity {humidity:.0f}% — fire risk elevated.", "ts": ts})

    # Wind
    if wind >= 20:
        alerts.append({"level":"danger",  "type":"💨 Gale Force Wind", "msg": f"Wind {wind:.1f} m/s — dangerous for outdoor activity.", "ts": ts})
    elif wind >= 12:
        alerts.append({"level":"warning", "type":"💨 Strong Wind",     "msg": f"Wind {wind:.1f} m/s — caution outdoors.", "ts": ts})

    # Rain
    if rain >= 15:
        alerts.append({"level":"danger",  "type":"🌧 Heavy Rain",      "msg": f"Precipitation {rain:.1f} mm/h — flash flood risk.", "ts": ts})
    elif rain >= 7:
        alerts.append({"level":"warning", "type":"🌧 Moderate Rain",   "msg": f"Precipitation {rain:.1f} mm/h.", "ts": ts})

    # Pressure (storm indicator)
    if pressure < 990:
        alerts.append({"level":"danger",  "type":"📉 Very Low Pressure","msg": f"Pressure {pressure:.0f} hPa — severe storm approaching.", "ts": ts})
    elif pressure < 1000:
        alerts.append({"level":"warning", "type":"📉 Low Pressure",    "msg": f"Pressure {pressure:.0f} hPa — deteriorating weather.", "ts": ts})

    # AQI / air quality
    aqi_desc, _ = get_aqi_description(aqi)
    if aqi >= 201:
        alerts.append({"level":"danger",  "type":"🌫 Very Unhealthy Air","msg": f"AQI {aqi} ({aqi_desc}) — avoid all outdoor activity.", "ts": ts})
    elif aqi >= 151:
        alerts.append({"level":"danger",  "type":"🌫 Unhealthy Air",   "msg": f"AQI {aqi} ({aqi_desc}) — sensitive groups stay indoors.", "ts": ts})
    elif aqi >= 101:
        alerts.append({"level":"warning", "type":"🌫 Moderate Air",    "msg": f"AQI {aqi} ({aqi_desc}) — sensitive individuals take care.", "ts": ts})

    # PM2.5
    if pm25 >= 55:
        alerts.append({"level":"danger",  "type":"🔬 PM2.5 Hazardous", "msg": f"PM2.5 {pm25:.1f} μg/m³ — wear N95 mask.", "ts": ts})

    # CO
    if co >= 10:
        alerts.append({"level":"danger",  "type":"☠ CO Elevated",      "msg": f"Carbon Monoxide {co:.1f} mg/m³ — ventilate spaces.", "ts": ts})

    # High risk scores
    for risk_name, score in risk_scores.items():
        if score >= 0.75:
            alerts.append({"level":"danger",  "type":f"⚠ {risk_name} Risk High",
                           "msg": f"{risk_name} probability {score*100:.0f}% — take precautions.", "ts": ts})
        elif score >= 0.55:
            alerts.append({"level":"warning", "type":f"⚠ {risk_name} Risk Moderate",
                           "msg": f"{risk_name} probability {score*100:.0f}%.", "ts": ts})

    if not alerts:
        alerts.append({"level":"ok", "type":"✅ All Clear",
                       "msg": "No environmental hazards detected at this time.", "ts": ts})

    return alerts
