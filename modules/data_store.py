"""
data_store.py
─────────────
Session-state based real-time data buffer.
Accumulates API readings across Streamlit reruns so we build a growing
live history without a database.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from datetime import datetime

# Maximum data points to keep in memory (≈ 24 h at 5-min intervals)
MAX_ROWS = 288


def _ensure(key: str, default):
    if key not in st.session_state:
        st.session_state[key] = default


def init_store():
    """Initialise all session-state buffers on first run."""
    _ensure("weather_history",     [])   # list[dict]
    _ensure("aq_history",          [])   # list[dict]
    _ensure("alert_history",       [])   # list[dict]
    _ensure("last_fetch_ts",       None) # datetime | None
    _ensure("fetch_count",         0)


def append_weather(record: dict):
    """Append a processed weather dict and trim to MAX_ROWS."""
    record = dict(record)
    record["_ts"] = datetime.now()
    st.session_state.weather_history.append(record)
    st.session_state.weather_history = st.session_state.weather_history[-MAX_ROWS:]


def append_air_quality(record: dict):
    record = dict(record)
    record["_ts"] = datetime.now()
    st.session_state.aq_history.append(record)
    st.session_state.aq_history = st.session_state.aq_history[-MAX_ROWS:]


def append_alerts(alerts: list[dict]):
    ts = datetime.now()
    for a in alerts:
        entry = dict(a)
        entry["_ts"] = ts
        st.session_state.alert_history.append(entry)
    # keep last 100 alerts
    st.session_state.alert_history = st.session_state.alert_history[-100:]


def weather_df() -> pd.DataFrame | None:
    if not st.session_state.weather_history:
        return None
    df = pd.DataFrame(st.session_state.weather_history)
    df.set_index("_ts", inplace=True)
    return df


def aq_df() -> pd.DataFrame | None:
    if not st.session_state.aq_history:
        return None
    df = pd.DataFrame(st.session_state.aq_history)
    df.set_index("_ts", inplace=True)
    return df


def mark_fetch():
    st.session_state.last_fetch_ts = datetime.now()
    st.session_state.fetch_count   = st.session_state.get("fetch_count", 0) + 1


def seconds_since_fetch() -> float | None:
    ts = st.session_state.get("last_fetch_ts")
    if ts is None:
        return None
    return (datetime.now() - ts).total_seconds()
