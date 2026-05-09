---
title: EcoSense AI Environment Monitoring
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.32.0"
app_file: app.py
pinned: false
---
<p align="center">
  <img src="https://img.icons8.com/color/96/earth-planet.png" width="90"/>
</p>

<h1 align="center">🌍 EcoSense AI — Environmental Intelligence Platform</h1>

<p align="center">
  <b>Real-time environmental monitoring, AI-powered forecasting, and intelligent risk alerting</b><br/>
  <sub>Powered by OpenWeatherMap · Built with Streamlit · Deployed on Hugging Face Spaces</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.28%2B-ff4b4b?logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-Interactive-3f4f75?logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenWeatherMap-API-eb6e4b"/>
  <img src="https://img.shields.io/badge/License-MIT-green"/>
</p>

---

## 🚀 What's New in v2 (Industry-Grade)

| Area | Improvement |
|------|-------------|
| **UI** | Full dark theme, glassmorphism cards, animated gradient header |
| **Performance** | `@st.cache_data` / `@st.cache_resource` — data cached for 10 min |
| **Reliability** | Automatic **retry with exponential back-off** on API failures (tenacity) |
| **Architecture** | Separated `ui_styles.py` + `ui_components.py` — zero inline CSS in app logic |
| **Config** | Unified `config.yaml` — single source of truth for thresholds, API, UI |
| **Error Handling** | Graceful degradation — falls back to Demo Mode when API key is missing |

---

## 🧠 Overview

EcoSense AI is a production-ready, AI-driven environmental dashboard that:

- 📡 Fetches **real-time weather + air-quality data** from OpenWeatherMap
- 🤖 Runs **AI/ML prediction models** for temperature forecasting & disaster risk
- 🚨 Fires **smart threshold alerts** for pollution, wind, heat, and precipitation
- 📊 Provides **interactive visualisations** — time-series, heatmaps, daily patterns
- 🌐 Runs on **Hugging Face Spaces** with zero-config secrets management

---

## 📁 Project Structure

```
AI-ENVIRONMENT-MONITORING/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Pinned dependencies
├── config/
│   ├── config.yaml            # Centralised configuration
│   ├── .env                   # Local secrets (git-ignored)
│   └── .env.template          # Template for onboarding
├── modules/
│   ├── data_fetcher.py        # OpenWeatherMap API client (with retry)
│   ├── data_processor.py      # Raw → structured data transformations
│   ├── prediction_engine.py   # ML model inference (LSTM / RF)
│   ├── alert_system.py        # Threshold-based alert generation
│   ├── feature_engineer.py    # Feature extraction for ML
│   ├── model_trainer.py       # Model training utilities
│   ├── aqi_calculator.py      # EPA AQI calculation
│   ├── utils.py               # Sample data & helper functions
│   ├── ui_styles.py           # Centralised dark-theme CSS
│   └── ui_components.py       # Reusable Streamlit components
├── data/
│   ├── historical_weather.csv
│   ├── air_quality_samples.csv
│   └── flood_data.csv
└── tests/
    ├── test_data_processor.py
    ├── test_model_trainer.py
    └── test_prediction_engine.py
```

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/GouravSinghThakur/AI-Environment-Monitoring.git
cd AI-ENVIRONMENT-MONITORING

# 2. Create & activate virtual environment
python -m venv .venv && .venv\Scripts\activate   # Windows
# python -m venv .venv && source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp config/.env.template config/.env
# Edit config/.env and set OPENWEATHERMAP_API_KEY=<your_key>

# 5. Run the dashboard
streamlit run app.py
```

> **No API key?** Enable **Demo Mode** in the sidebar — the app runs fully on generated sample data.

---

## 🔐 Hugging Face Deployment

```bash
# Push to your HF Space
git remote add hf https://huggingface.co/spaces/<username>/<space-name>
git push hf main
```

Set `OPENWEATHERMAP_API_KEY` in **Settings → Repository secrets** — never commit it to the repo.

---

## 🏗 System Architecture

```
OpenWeatherMap API
       │
  data_fetcher.py  ──(retry / timeout)──►  Raw JSON
       │
  data_processor.py ──────────────────►  Structured DataFrames
       │                    │
prediction_engine.py   alert_system.py
       │                    │
       └──────────┬──────────┘
                  ▼
           Streamlit app.py
          (cached, dark UI)
```

---

## 📊 Dashboard Tabs

| Tab | Content |
|-----|---------|
| **📡 Live Conditions** | Temperature, humidity, wind, AQI metric cards + detailed pollutant table |
| **🔮 Forecast** | 5-day temperature & precipitation charts |
| **🤖 AI Predictions** | Temperature trend with CI bands + 4 environmental risk gauges |
| **📊 Data Analysis** | Time-series, correlation heatmaps, daily patterns, statistical summaries |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.28+, Plotly 5.15+ |
| ML / AI | scikit-learn, (optional) TensorFlow/Keras |
| Data | pandas, NumPy, SciPy |
| API Client | requests + tenacity (retry) |
| Config | PyYAML + python-dotenv |
| Deploy | Hugging Face Spaces |

---

## 📄 License

MIT © 2025 Gourav Singh Thakur
