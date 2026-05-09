"""
app.py — EcoSense AI · Real-Time Environmental Dashboard v3
"""
import os, sys, logging, yaml, time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv

<<<<<<< Updated upstream
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
=======
_BASE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE, "config", ".env"))
sys.path.insert(0, _BASE)
>>>>>>> Stashed changes

with open(os.path.join(_BASE, "config", "config.yaml")) as _f:
    config = yaml.safe_load(_f)

<<<<<<< Updated upstream
from modules.data_fetcher import fetch_current_weather, fetch_air_quality, fetch_weather_forecast, get_location_by_name
from modules.data_processor import process_weather_data, process_air_quality_data, process_forecast_data
from modules.prediction_engine import PredictionEngine
from modules.alert_system import AlertSystem
from modules.utils import (
    load_sample_data, 
    create_time_series_plot, 
    create_correlation_heatmap,
    format_weather_icon_url,
    celsius_to_fahrenheit,
    get_aqi_description
)

# Load environment variables and configuration
load_dotenv()
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Check if API key is available
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
if not API_KEY:
    st.error("OpenWeatherMap API key not found. Please add it to the .env file.")
    st.stop()

# Initialize prediction engine and alert system
prediction_engine = PredictionEngine()
alert_system = AlertSystem()

# Set page configuration
=======
>>>>>>> Stashed changes
st.set_page_config(
    page_title="EcoSense AI · Live Dashboard",
    page_icon="🌍", layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from modules.ui_styles     import DARK_CSS, PLOTLY_THEME
from modules.ui_components import metric_card, alert_box, risk_gauge, section_header
from modules.data_fetcher  import (fetch_current_weather, fetch_air_quality,
                                   fetch_weather_forecast, get_location_by_name)
from modules.data_processor import (process_weather_data, process_air_quality_data,
                                    process_forecast_data)
from modules.data_store    import (init_store, append_weather, append_air_quality,
                                   append_alerts, weather_df, aq_df, mark_fetch,
                                   seconds_since_fetch)
from modules.realtime_engine    import (compute_risk_scores, predict_temperature,
                                         generate_dynamic_alerts)
from modules.historical_fetcher import load_both as load_history
from modules.ml_trainer         import train_models, predict_with_model
from modules.utils              import load_sample_data, celsius_to_fahrenheit, get_aqi_description

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_OK = True
except ImportError:
    AUTOREFRESH_OK = False

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")

# ── Session init ──────────────────────────────────────────────────────────────
init_store()
if "lat" not in st.session_state:
    st.session_state.lat  = config["ui"]["default_location"]["lat"]
    st.session_state.lon  = config["ui"]["default_location"]["lon"]
    st.session_state.city = config["ui"]["default_location"]["city"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 EcoSense AI")
    st.markdown("<small style='color:#475569'>Real-Time Environmental Dashboard v3</small>",
                unsafe_allow_html=True)
    st.divider()

    loc_method = st.radio("📍 Location", ["City Name", "Coordinates"], horizontal=True)
    if loc_method == "City Name":
        city_in = st.text_input("City", value=st.session_state.city)
        if st.button("🔍 Search", use_container_width=True):
            res = get_location_by_name(city_in)
            if res:
                st.session_state.lat, st.session_state.lon = res
                st.session_state.city = city_in
                st.cache_data.clear()
                st.success(f"📌 {city_in}")
            else:
                st.error("City not found.")
    else:
        st.session_state.lat = st.number_input("Latitude",  value=st.session_state.lat,  format="%.4f")
        st.session_state.lon = st.number_input("Longitude", value=st.session_state.lon, format="%.4f")

    st.divider()
    units        = st.selectbox("🌡 Units", ["Celsius (°C)", "Fahrenheit (°F)"])
    forecast_hrs = st.slider("⏱ Forecast horizon (hrs)", 12, 120, 48, 12)
    demo_mode    = st.checkbox("🧪 Demo mode", value=not bool(API_KEY))

    refresh_mins = st.select_slider("🔄 Auto-refresh", [1, 2, 5, 10, 15, 30], value=5)
    if AUTOREFRESH_OK:
        count = st_autorefresh(interval=refresh_mins * 60 * 1000, key="autorefresh")
    else:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()
    ver = config.get("app", {}).get("version", "3.0")
    st.markdown(f"<small style='color:#475569'>v{ver}</small>", unsafe_allow_html=True)

lat, lon   = st.session_state.lat, st.session_state.lon
use_f      = "Fahrenheit" in units
temp_unit  = "°F" if use_f else "°C"
to_disp    = lambda c: round(celsius_to_fahrenheit(c) if use_f else c, 1)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='hero-header'>🌍 EcoSense AI — Live Environmental Intelligence</div>",
            unsafe_allow_html=True)

elapsed = seconds_since_fetch()
fetch_n = st.session_state.get("fetch_count", 0)
next_in = max(0, refresh_mins * 60 - (elapsed or 0))
c1, c2, c3 = st.columns(3)
c1.markdown(f"<p style='text-align:center;color:#64748b'>📍 {st.session_state.city} · {lat:.3f}°, {lon:.3f}°</p>", unsafe_allow_html=True)
c2.markdown(f"<p style='text-align:center;color:#64748b'>🕐 {datetime.now().strftime('%H:%M:%S, %d %b %Y')}</p>", unsafe_allow_html=True)
c3.markdown(f"<p style='text-align:center;color:#64748b'>🔁 Fetch #{fetch_n} · Next refresh in {int(next_in)}s</p>", unsafe_allow_html=True)

if not API_KEY and not demo_mode:
    st.warning("⚠️ No API key — enable Demo Mode or add OPENWEATHERMAP_API_KEY to config/.env")

# ── Live data fetch ───────────────────────────────────────────────────────────
@st.cache_data(ttl=refresh_mins * 60, show_spinner=False)
def live_weather(lat, lon): return process_weather_data(fetch_current_weather(lat, lon))

@st.cache_data(ttl=refresh_mins * 60, show_spinner=False)
def live_aq(lat, lon):      return process_air_quality_data(fetch_air_quality(lat, lon))

@st.cache_data(ttl=refresh_mins * 60, show_spinner=False)
def live_forecast(lat, lon):return process_forecast_data(fetch_weather_forecast(lat, lon))

if demo_mode:
    sample_w  = load_sample_data("weather")
    sample_aq = load_sample_data("air_quality")
    weather_data     = sample_w.iloc[-1].to_dict()
    air_quality_data = sample_aq.iloc[-1].to_dict()
    weather_data.setdefault("weather_description", "Clear sky")
    weather_data.setdefault("rain_1h", float(np.random.exponential(0.3)))
    weather_data["temperature"] += float(np.random.normal(0, 0.5))   # slight variation
    air_quality_data["aqi"]     = int(max(1, air_quality_data.get("aqi", 60) + np.random.randint(-5, 6)))
    forecast_df = sample_w
else:
    with st.spinner("📡 Fetching live data…"):
        weather_data     = live_weather(lat, lon)
        air_quality_data = live_aq(lat, lon)
        forecast_df      = live_forecast(lat, lon)

# Accumulate history
if weather_data:
    append_weather(weather_data)
    mark_fetch()
if air_quality_data:
    append_air_quality(air_quality_data)

w_hist = weather_df()
aq_hist = aq_df()

# ── 90-day historical data + model training (once per session) ────────────────
@st.cache_resource(show_spinner=False)
def get_historical_and_models(_lat, _lon, _api_key):
    """Fetch 90-day history and train ML models. Cached for the whole session."""
    wx_h, aq_h = load_history(_lat, _lon, _api_key, days=90)
    models = train_models(wx_h, aq_h)
    return wx_h, aq_h, models

with st.spinner("📚 Loading 90-day history & training AI models (first run only)…"):
    wx_hist_90, aq_hist_90, ml_models = get_historical_and_models(lat, lon, API_KEY)

# Merge live session readings into the 90-day history for latest context
def _drop_dict_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns that contain dict values (unhashable, breaks dedup)."""
    bad = [c for c in df.columns if df[c].apply(lambda x: isinstance(x, dict)).any()]
    return df.drop(columns=bad, errors="ignore")

if w_hist is not None and wx_hist_90 is not None:
    wx_hist_90 = pd.concat([wx_hist_90, _drop_dict_cols(w_hist)]).sort_index()
    wx_hist_90 = wx_hist_90[~wx_hist_90.index.duplicated(keep="last")]
if aq_hist is not None and aq_hist_90 is not None:
    aq_hist_90 = pd.concat([aq_hist_90, _drop_dict_cols(aq_hist)]).sort_index()
    aq_hist_90 = aq_hist_90[~aq_hist_90.index.duplicated(keep="last")]

# ── Helper functions ─────────────────────────────────────────────────────────
def _risk_driver(risk_name: str, w: dict, aq: dict) -> str:
    drivers = {
        "Flood":        f"Rain {w.get('rain_1h',0):.1f}mm, Humidity {w.get('humidity',0):.0f}%, P {w.get('pressure',0):.0f}hPa",
        "Storm":        f"Wind {w.get('wind_speed',0):.1f}m/s, P {w.get('pressure',0):.0f}hPa",
        "Heatwave":     f"Temp {w.get('temperature',0):.1f}°C, Humidity {w.get('humidity',0):.0f}%",
        "Air Pollution":f"AQI {aq.get('aqi',0)}, PM2.5 {aq.get('pm2_5',0):.1f}μg/m³",
    }
    return drivers.get(risk_name, "—")


# ── Compute AI predictions ─────────────────────────────────────────────────────
risk_scores    = {}
dynamic_alerts = []
ml_predictions = {}
temp_pred_df   = None
aqi_pred_df    = None

if weather_data and air_quality_data:
    risk_scores    = compute_risk_scores(weather_data, air_quality_data, wx_hist_90)
    dynamic_alerts = generate_dynamic_alerts(weather_data, air_quality_data, risk_scores)
    # Use ML models trained on 90-day data
    ml_predictions = predict_with_model(ml_models, wx_hist_90, aq_hist_90, forecast_hrs)
    temp_pred_df   = ml_predictions.get("temperature")
    aqi_pred_df    = ml_predictions.get("aqi")
    append_alerts(dynamic_alerts)

# ── LIVE ALERT BANNER (top of page) ──────────────────────────────────────────
danger_alerts = [a for a in dynamic_alerts if a["level"] == "danger"]
if danger_alerts:
    st.error(f"🚨 **{len(danger_alerts)} ACTIVE DANGER ALERT(S)** — {danger_alerts[0]['type']}: {danger_alerts[0]['msg']}")
elif [a for a in dynamic_alerts if a["level"] == "warning"]:
    warn_list = [a for a in dynamic_alerts if a["level"] == "warning"]
    st.warning(f"⚠️ **{len(warn_list)} Warning(s)** — {warn_list[0]['type']}: {warn_list[0]['msg']}")
else:
    st.success("✅ All environmental parameters within safe limits.")

# ════════════════════════════════════════════════════════════════════════════════
tabs = st.tabs(["📡 Live Conditions", "🔮 Forecast", "🤖 AI Predictions & Alerts", "📊 Analysis"])

# ── TAB 0: Live Conditions ────────────────────────────────────────────────────
with tabs[0]:
    section_header("Current Weather & Air Quality")
    if weather_data and air_quality_data:
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            metric_card("Temperature",  f"{to_disp(weather_data['temperature'])}{temp_unit}", "🌡")
            metric_card("Feels Like",   f"{to_disp(weather_data.get('feels_like', weather_data['temperature']))}{temp_unit}", "🤔")
        with mc2:
            metric_card("Humidity",     f"{weather_data['humidity']}%",        "💧")
            metric_card("Pressure",     f"{weather_data['pressure']} hPa",     "📊")
        with mc3:
            metric_card("Wind Speed",   f"{weather_data['wind_speed']} m/s",   "💨",
                        f"Dir {weather_data.get('wind_direction',0)}°")
            metric_card("Rain (1h)",    f"{weather_data.get('rain_1h',0):.1f} mm", "🌧")
        with mc4:
            aqi = air_quality_data.get("aqi", 0)
            desc, _ = get_aqi_description(aqi)
            metric_card("AQI",          str(aqi),                              "🌫", desc)
            metric_card("PM2.5",        f"{air_quality_data.get('pm2_5',0):.1f} μg/m³", "🔬")

        with st.expander("🔬 Full Pollutant Readings"):
            col_w, col_a = st.columns(2)
            with col_w:
                st.table(pd.DataFrame({
                    "Metric": ["Condition", "Min Temp", "Max Temp", "Clouds", "Sunrise", "Sunset"],
                    "Value":  [
                        weather_data.get("weather_description","—").title(),
                        f"{to_disp(weather_data.get('temp_min', weather_data['temperature']))}{temp_unit}",
                        f"{to_disp(weather_data.get('temp_max', weather_data['temperature']))}{temp_unit}",
                        f"{weather_data.get('clouds',0)}%",
                        weather_data.get("sunrise","—"), weather_data.get("sunset","—"),
                    ],
                }))
            with col_a:
                st.table(pd.DataFrame({
                    "Pollutant": ["CO (mg/m³)","NO₂","O₃","SO₂","PM2.5","PM10","NH₃"],
                    "Value":     [f"{air_quality_data.get(k,0):.2f}" for k in
                                  ["co","no2","o3","so2","pm2_5","pm10","nh3"]],
                }))
    else:
        st.error("❌ Could not fetch live data.")

# ── TAB 1: Forecast ───────────────────────────────────────────────────────────
with tabs[1]:
    section_header("5-Day Weather Forecast")
    if forecast_df is not None and not forecast_df.empty:
        tc = "temperature"
        y_fc = forecast_df[tc].apply(celsius_to_fahrenheit) if use_f else forecast_df[tc]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df.index, y=y_fc, name=f"Temp ({temp_unit})",
                                 line=dict(color="#00d4ff", width=2.5),
                                 fill="tozeroy", fillcolor="rgba(0,212,255,0.07)"))
        if "feels_like" in forecast_df.columns:
            fl = forecast_df["feels_like"].apply(celsius_to_fahrenheit) if use_f else forecast_df["feels_like"]
            fig.add_trace(go.Scatter(x=forecast_df.index, y=fl, name="Feels Like",
                                     line=dict(color="#7c3aed", dash="dash")))
        fig.update_layout(**PLOTLY_THEME, title="Temperature Forecast",
                          yaxis_title=f"Temperature ({temp_unit})", hovermode="x unified", height=360)
        st.plotly_chart(fig, use_container_width=True)

        if "rain_3h" in forecast_df.columns:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=forecast_df.index, y=forecast_df["rain_3h"],
                                  name="Rain (mm)", marker_color="rgba(0,212,255,0.55)"))
            if "probability" in forecast_df.columns:
                fig2.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["probability"],
                                          name="Probability %", line=dict(color="#f59e0b"), yaxis="y2"))
                fig2.update_layout(yaxis2=dict(title="Prob %", overlaying="y", side="right", range=[0,100]))
            fig2.update_layout(**PLOTLY_THEME, title="Precipitation", height=280, hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

        cols_ = [c for c in ["weather_main","humidity","wind_speed","probability"] if c in forecast_df.columns]
        tbl   = forecast_df[cols_].copy()
        tbl.index = tbl.index.strftime("%d %b %H:%M")
        st.dataframe(tbl, use_container_width=True)
    else:
        st.error("Forecast data unavailable.")

# ── TAB 2: AI Predictions & Alerts ───────────────────────────────────────────
with tabs[2]:
    section_header("AI Predictions & Real-Time Alerts")

    if weather_data and air_quality_data:

        # Temperature AI prediction
        temp_src = ml_predictions.get("temp_source", "Fallback")
        st.markdown(f"#### 🤖 AI Temperature Forecast  — *{temp_src}*")
        if temp_pred_df is not None:
            fig = go.Figure()
            # Show 90-day history (last 7 days for readability)
            if wx_hist_90 is not None and "temperature" in wx_hist_90.columns:
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
                hist7  = wx_hist_90.loc[wx_hist_90.index >= cutoff]
                hist_y = hist7["temperature"].apply(celsius_to_fahrenheit) if use_f else hist7["temperature"]
                fig.add_trace(go.Scatter(x=hist7.index, y=hist_y, name="90-day History (last 7d)",
                                         line=dict(color="#00d4ff", width=1.5)))
            pred_y = temp_pred_df["predicted"].apply(celsius_to_fahrenheit) if use_f else temp_pred_df["predicted"]
            up_y   = temp_pred_df["upper"].apply(celsius_to_fahrenheit)     if use_f else temp_pred_df["upper"]
            lo_y   = temp_pred_df["lower"].apply(celsius_to_fahrenheit)     if use_f else temp_pred_df["lower"]
            fig.add_trace(go.Scatter(x=temp_pred_df.index, y=pred_y, name="AI Predicted",
                                     line=dict(color="#f59e0b", dash="dash", width=2.5)))
            fig.add_trace(go.Scatter(x=temp_pred_df.index, y=up_y, line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=temp_pred_df.index, y=lo_y, fill="tonexty",
                                     fillcolor="rgba(245,158,11,0.10)", line=dict(width=0),
                                     name="Uncertainty Band"))
            fig.update_layout(**PLOTLY_THEME, title=f"AI Temperature Forecast — Next {forecast_hrs}h",
                              yaxis_title=f"Temperature ({temp_unit})", hovermode="x unified", height=400)
            st.plotly_chart(fig, use_container_width=True)

<<<<<<< Updated upstream
# Footer
st.markdown("---")
st.markdown("### AI Environment Monitoring System")
st.markdown("Developed for environmental monitoring and prediction using AI techniques.")
st.markdown("© 2025 AI Environment Monitoring System")
=======
            pc1, pc2, pc3, pc4 = st.columns(4)
            pc1.metric("Current",       f"{to_disp(weather_data['temperature'])}{temp_unit}")
            pc2.metric("Predicted High (24h)", f"{to_disp(temp_pred_df['predicted'][:24].max())}{temp_unit}")
            pc3.metric("Predicted Low (24h)",  f"{to_disp(temp_pred_df['predicted'][:24].min())}{temp_unit}")
            m = ml_models.get("metrics", {}).get("temperature", {})
            pc4.metric("Model MAE", f"{m.get('mae','—')}{temp_unit}", f"R² {m.get('r2','—')}")

        st.divider()

        # AQI AI prediction
        aqi_src = ml_predictions.get("aqi_source", "")
        if aqi_pred_df is not None:
            st.markdown(f"#### 🌫 AI AQI Forecast — *{aqi_src}*")
            fig_aqi = go.Figure()
            if aq_hist_90 is not None and "aqi" in aq_hist_90.columns:
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
                aq7 = aq_hist_90.loc[aq_hist_90.index >= cutoff]
                fig_aqi.add_trace(go.Scatter(x=aq7.index, y=aq7["aqi"],
                                             name="90-day History (last 7d)",
                                             line=dict(color="#10b981", width=1.5)))
            fig_aqi.add_trace(go.Scatter(x=aqi_pred_df.index, y=aqi_pred_df["predicted"],
                                         name="AI Predicted AQI",
                                         line=dict(color="#f59e0b", dash="dash", width=2.5)))
            fig_aqi.add_trace(go.Scatter(x=aqi_pred_df.index, y=aqi_pred_df["upper"],
                                         line=dict(width=0), showlegend=False))
            fig_aqi.add_trace(go.Scatter(x=aqi_pred_df.index, y=aqi_pred_df["lower"],
                                         fill="tonexty", fillcolor="rgba(245,158,11,0.10)",
                                         line=dict(width=0), name="Uncertainty Band"))
            fig_aqi.add_hline(y=100, line_dash="dash", line_color="#ef4444",
                              annotation_text="Unhealthy threshold (100)")
            fig_aqi.add_hline(y=50,  line_dash="dot",  line_color="#10b981",
                              annotation_text="Good (50)")
            fig_aqi.update_layout(**PLOTLY_THEME, title=f"AI AQI Forecast — Next {forecast_hrs}h",
                                  yaxis_title="AQI", hovermode="x unified", height=360)
            st.plotly_chart(fig_aqi, use_container_width=True)

            ac1, ac2, ac3, ac4 = st.columns(4)
            ac1.metric("Current AQI",   str(air_quality_data.get("aqi", "—")))
            ac2.metric("Predicted Peak (24h)", f"{int(aqi_pred_df['predicted'][:24].max())}")
            ac3.metric("Predicted Low (24h)",  f"{int(aqi_pred_df['predicted'][:24].min())}")
            m2 = ml_models.get("metrics", {}).get("aqi", {})
            ac4.metric("Model MAE", f"{m2.get('mae','—')}", f"R² {m2.get('r2','—')}")

        st.divider()

        # Risk gauges
        st.markdown("#### ⚠️ Real-Time Environmental Risk Assessment")
        gcols = st.columns(4)
        for col, (name, score) in zip(gcols, risk_scores.items()):
            with col:
                lvl = "🔴 HIGH" if score >= 0.7 else ("🟡 MEDIUM" if score >= 0.4 else "🟢 LOW")
                st.plotly_chart(risk_gauge(name, score), use_container_width=True)
                st.markdown(f"<p style='text-align:center;font-size:.8rem;color:#94a3b8'>{lvl} · {score*100:.0f}%</p>",
                            unsafe_allow_html=True)

        risk_df = pd.DataFrame([
            {"Risk": k, "Score": f"{v*100:.0f}%",
             "Level": "🔴 High" if v >= 0.7 else ("🟡 Medium" if v >= 0.4 else "🟢 Low"),
             "Driver": _risk_driver(k, weather_data, air_quality_data)}
            for k, v in risk_scores.items()
        ])
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

        st.divider()

        # Dynamic alerts
        st.markdown(f"#### 🚨 Live Alerts — updated {datetime.now().strftime('%H:%M:%S')}")
        for a in dynamic_alerts:
            if a["level"] == "danger":
                st.error(f"**{a['type']}** — {a['msg']}  `{a['ts']}`")
            elif a["level"] == "warning":
                st.warning(f"**{a['type']}** — {a['msg']}  `{a['ts']}`")
            else:
                st.success(f"**{a['type']}** — {a['msg']}")

        # Alert history
        if st.session_state.alert_history:
            with st.expander(f"📋 Alert History ({len(st.session_state.alert_history)} events)"):
                hist_df = pd.DataFrame(st.session_state.alert_history)
                hist_df["_ts"] = hist_df["_ts"].astype(str)
                st.dataframe(hist_df[["_ts","level","type","msg"]].rename(
                    columns={"_ts":"Time","level":"Level","type":"Alert","msg":"Message"}),
                    use_container_width=True, hide_index=True)
    else:
        st.error("Live data unavailable for predictions.")

# ── TAB 3: Analysis ───────────────────────────────────────────────────────────
with tabs[3]:
    section_header("Historical Data Analysis")

    src = st.radio("Data source", ["90-Day Real History", "Live Session History", "Sample Dataset"], horizontal=True)
    if src == "90-Day Real History":
        fw = wx_hist_90 if wx_hist_90 is not None else pd.DataFrame()
        fa = aq_hist_90 if aq_hist_90 is not None else pd.DataFrame()
        rows_w = len(fw); rows_a = len(fa)
        st.caption(f"📊 Using fetched historical data: **{rows_w}** weather rows · **{rows_a}** AQ rows spanning ~90 days")
    elif src == "Live Session History" and w_hist is not None:
        fw = w_hist; fa = aq_hist if aq_hist is not None else pd.DataFrame()
    else:
        fw = load_sample_data("weather"); fa = load_sample_data("air_quality")

    viz = st.selectbox("Visualization", ["Time Series", "Correlation Heatmap", "Daily Patterns", "Statistical Summary"])

    if not fw.empty:
        if viz == "Time Series":
            dtype = st.selectbox("Dataset", ["Weather", "Air Quality"])
            df    = fw if dtype == "Weather" else fa
            if not df.empty:
                cols_ = st.multiselect("Variables", df.select_dtypes("number").columns.tolist(),
                                       default=df.select_dtypes("number").columns[:3].tolist())
                if cols_:
                    fig = px.line(df, x=df.index, y=cols_, title=f"{dtype} Time Series",
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(**PLOTLY_THEME, hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)

        elif viz == "Correlation Heatmap":
            dtype = st.selectbox("Dataset", ["Weather", "Air Quality"])
            df    = fw if dtype == "Weather" else fa
            if not df.empty:
                corr = df.select_dtypes("number").corr()
                fig  = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                                 title="Correlation Matrix")
                fig.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)

        elif viz == "Daily Patterns":
            dtype = st.selectbox("Dataset", ["Weather", "Air Quality"])
            df    = fw if dtype == "Weather" else fa
            if not df.empty and len(df) >= 3:
                var   = st.selectbox("Variable", df.select_dtypes("number").columns.tolist())
                df    = df.copy(); df["hour"] = df.index.hour
                stats = df.groupby("hour")[var].agg(["mean","min","max"])
                fig   = go.Figure()
                fig.add_trace(go.Scatter(x=stats.index, y=stats["mean"], name="Mean",
                                         line=dict(color="#00d4ff", width=2)))
                fig.add_trace(go.Scatter(x=stats.index, y=stats["max"], name="Max",
                                         line=dict(color="#ef4444", dash="dash")))
                fig.add_trace(go.Scatter(x=stats.index, y=stats["min"], name="Min",
                                         fill="tonexty", fillcolor="rgba(0,212,255,0.07)",
                                         line=dict(color="#10b981", dash="dash")))
                fig.update_layout(**PLOTLY_THEME, title=f"Daily Pattern — {var}",
                                  xaxis_title="Hour", yaxis_title=var)
                st.plotly_chart(fig, use_container_width=True)

        elif viz == "Statistical Summary":
            dtype = st.selectbox("Dataset", ["Weather", "Air Quality"])
            df    = (fw if dtype == "Weather" else fa).select_dtypes("number")
            if not df.empty:
                stats = df.describe().T
                stats["range"] = stats["max"] - stats["min"]
                stats["cv%"]   = (stats["std"] / stats["mean"].abs() * 100).round(1)
                st.dataframe(stats.style.format("{:.2f}"), use_container_width=True)
    else:
        st.info("No data yet. Collect a few readings first.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='footer'>EcoSense AI v3 · Real-Time Environmental Intelligence · "
    "© 2025 Gourav Singh Thakur</div>",
    unsafe_allow_html=True,
)
