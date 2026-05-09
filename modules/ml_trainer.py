"""
ml_trainer.py (v2)
──────────────────
Trains scikit-learn models on the 90-day historical dataset and generates
real AI predictions for temperature and AQI.

Models:
  Temperature : RandomForestRegressor (tabular features)
  AQI         : RandomForestRegressor (tabular features)

Both models are cached in memory via session-state so training only happens
once per app session (or when the historical data changes).
"""
from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ── Feature engineering ────────────────────────────────────────────────────────

def _make_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract time + lag features from a time-indexed DataFrame."""
    d = df.copy()
    idx = d.index
    d["hour"]       = idx.hour
    d["dayofyear"]  = idx.dayofyear
    d["dayofweek"]  = idx.dayofweek
    d["month"]      = idx.month
    d["hour_sin"]   = np.sin(2 * np.pi * d["hour"]      / 24)
    d["hour_cos"]   = np.cos(2 * np.pi * d["hour"]      / 24)
    d["doy_sin"]    = np.sin(2 * np.pi * d["dayofyear"] / 365)
    d["doy_cos"]    = np.cos(2 * np.pi * d["dayofyear"] / 365)
    return d


def _add_lags(df: pd.DataFrame, col: str, lags=(1, 3, 6, 12, 24)) -> pd.DataFrame:
    for lag in lags:
        df[f"{col}_lag{lag}"] = df[col].shift(lag)
    return df


# ── Train models ───────────────────────────────────────────────────────────────

def train_models(wx_df: pd.DataFrame | None,
                 aq_df: pd.DataFrame | None) -> dict:
    """
    Train temperature + AQI RandomForest models on historical data.
    Returns dict with keys: 'temp_model', 'aqi_model', 'temp_features', 'aqi_features', 'metrics'
    """
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.preprocessing import StandardScaler

    result: dict = {"temp_model": None, "aqi_model": None,
                    "temp_features": [], "aqi_features": [], "metrics": {}}

    # ── Temperature model ──────────────────────────────────────────────────────
    if wx_df is not None and "temperature" in wx_df.columns and len(wx_df) > 100:
        try:
            df = _make_features(wx_df.copy())
            df = _add_lags(df, "temperature")
            if "humidity"   in df.columns: df = _add_lags(df, "humidity",   (1, 6, 24))
            if "wind_speed" in df.columns: df = _add_lags(df, "wind_speed", (1, 6))
            df.dropna(inplace=True)

            base_feats = ["hour_sin","hour_cos","doy_sin","doy_cos","month","dayofweek"]
            lag_feats  = [c for c in df.columns if "_lag" in c]
            extra      = [c for c in ["humidity","pressure","wind_speed","rain_1h","clouds"]
                          if c in df.columns]
            features   = base_feats + lag_feats + extra

            X = df[features].values
            y = df["temperature"].values
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.15, shuffle=False)

            model = RandomForestRegressor(n_estimators=120, max_depth=12,
                                          min_samples_leaf=4, n_jobs=-1, random_state=42)
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)
            mae  = mean_absolute_error(y_te, preds)
            r2   = r2_score(y_te, preds)

            result["temp_model"]    = model
            result["temp_features"] = features
            result["metrics"]["temperature"] = {"mae": round(mae, 2), "r2": round(r2, 3),
                                                "train_rows": len(X_tr)}
            logger.info("Temperature model trained — MAE %.2f°C, R² %.3f", mae, r2)
        except Exception as exc:
            logger.error("Temperature model training failed: %s", exc)

    # ── AQI model ──────────────────────────────────────────────────────────────
    if aq_df is not None and "aqi" in aq_df.columns and len(aq_df) > 100:
        try:
            df = _make_features(aq_df.copy())
            df = _add_lags(df, "aqi")
            for col in ["pm2_5","pm10","o3","co","no2","so2"]:
                if col in df.columns:
                    df = _add_lags(df, col, (1, 6, 24))
            df.dropna(inplace=True)

            base_feats = ["hour_sin","hour_cos","doy_sin","doy_cos","month","dayofweek"]
            lag_feats  = [c for c in df.columns if "_lag" in c]
            features   = base_feats + lag_feats

            X = df[features].values
            y = df["aqi"].values
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.15, shuffle=False)

            model = GradientBoostingRegressor(n_estimators=120, max_depth=5,
                                              learning_rate=0.08, random_state=42)
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)
            mae  = mean_absolute_error(y_te, preds)
            r2   = r2_score(y_te, preds)

            result["aqi_model"]    = model
            result["aqi_features"] = features
            result["metrics"]["aqi"] = {"mae": round(mae, 2), "r2": round(r2, 3),
                                        "train_rows": len(X_tr)}
            logger.info("AQI model trained — MAE %.1f, R² %.3f", mae, r2)
        except Exception as exc:
            logger.error("AQI model training failed: %s", exc)

    return result


# ── Prediction helpers ─────────────────────────────────────────────────────────

def _build_future_row(base_time: datetime, i: int,
                      last_vals: dict, feature_names: list) -> list:
    """Build a single feature row for hour `base_time + i hours`."""
    t   = base_time + timedelta(hours=i)
    row = {
        "hour":      t.hour,
        "dayofyear": t.timetuple().tm_yday,
        "dayofweek": t.weekday(),
        "month":     t.month,
        "hour_sin":  np.sin(2 * np.pi * t.hour      / 24),
        "hour_cos":  np.cos(2 * np.pi * t.hour      / 24),
        "doy_sin":   np.sin(2 * np.pi * t.timetuple().tm_yday / 365),
        "doy_cos":   np.cos(2 * np.pi * t.timetuple().tm_yday / 365),
    }
    row.update(last_vals)
    return [row.get(f, 0.0) for f in feature_names]


def predict_with_model(models: dict, wx_df: pd.DataFrame | None,
                       aq_df: pd.DataFrame | None,
                       hours: int = 48) -> dict:
    """
    Generate multi-step temperature and AQI forecasts using trained models.
    Falls back to physics-informed forecast if models are unavailable.
    """
    from modules.realtime_engine import predict_temperature as fallback_temp

    out   = {}
    now   = datetime.now()
    times = pd.date_range(start=now, periods=hours, freq="h")

    # ── Temperature ──────────────────────────────────────────────────────────
    temp_model = models.get("temp_model")
    if temp_model and wx_df is not None and len(wx_df) > 24:
        try:
            feats    = models["temp_features"]
            last_row = wx_df.tail(24).copy()
            last_row = _make_features(last_row)
            last_row = _add_lags(last_row, "temperature")
            for col in ["humidity","wind_speed"]:
                if col in last_row.columns:
                    last_row = _add_lags(last_row, col, (1, 6, 24))
            last_row.dropna(inplace=True)

            if not last_row.empty:
                last_vals = {f: last_row[f].iloc[-1] for f in feats if f in last_row.columns}
                pred_vals = []
                for i in range(hours):
                    row   = _build_future_row(now, i, last_vals, feats)
                    pred  = float(temp_model.predict([row])[0])
                    pred_vals.append(pred)
                    last_vals["temperature_lag1"] = pred
                    last_vals["temperature_lag3"] = pred_vals[-3] if len(pred_vals) >= 3 else pred
                    last_vals["temperature_lag6"] = pred_vals[-6] if len(pred_vals) >= 6 else pred

                uncertainty = 0.8 + np.arange(hours) * 0.03
                out["temperature"] = pd.DataFrame({
                    "predicted": pred_vals,
                    "upper":     np.array(pred_vals) + uncertainty,
                    "lower":     np.array(pred_vals) - uncertainty,
                }, index=times)
                out["temp_source"] = "RandomForest (90-day trained)"
        except Exception as exc:
            logger.error("RF temperature prediction failed: %s", exc)

    if "temperature" not in out:
        current_temp = wx_df["temperature"].iloc[-1] if wx_df is not None and len(wx_df) > 0 else 25.0
        mock_w = {"temperature": current_temp, "humidity": 60, "clouds": 30}
        out["temperature"] = fallback_temp(mock_w, wx_df, hours)
        out["temp_source"] = "Physics-informed fallback"

    # ── AQI ──────────────────────────────────────────────────────────────────
    aqi_model = models.get("aqi_model")
    if aqi_model and aq_df is not None and len(aq_df) > 24:
        try:
            feats    = models["aqi_features"]
            last_row = aq_df.tail(48).copy()
            last_row = _make_features(last_row)
            last_row = _add_lags(last_row, "aqi")
            for col in ["pm2_5","pm10","o3","co","no2","so2"]:
                if col in last_row.columns:
                    last_row = _add_lags(last_row, col, (1, 6, 24))
            last_row.dropna(inplace=True)

            if not last_row.empty:
                last_vals = {f: last_row[f].iloc[-1] for f in feats if f in last_row.columns}
                pred_vals = []
                for i in range(hours):
                    row  = _build_future_row(now, i, last_vals, feats)
                    pred = float(aqi_model.predict([row])[0])
                    pred = max(0, min(500, pred))
                    pred_vals.append(pred)
                    last_vals["aqi_lag1"] = pred
                    last_vals["aqi_lag3"] = pred_vals[-3] if len(pred_vals) >= 3 else pred
                    last_vals["aqi_lag6"] = pred_vals[-6] if len(pred_vals) >= 6 else pred

                out["aqi"] = pd.DataFrame({
                    "predicted": pred_vals,
                    "upper":     np.clip(np.array(pred_vals) * 1.15, 0, 500),
                    "lower":     np.clip(np.array(pred_vals) * 0.85, 0, 500),
                }, index=times)
                out["aqi_source"] = "GradientBoosting (90-day trained)"
        except Exception as exc:
            logger.error("RF AQI prediction failed: %s", exc)

    return out
