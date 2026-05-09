"""ui_components.py — Reusable Streamlit UI components."""
import streamlit as st
import plotly.graph_objects as go
from modules.ui_styles import PLOTLY_THEME, RISK_COLOR
from modules.utils import get_aqi_description, celsius_to_fahrenheit


def metric_card(label: str, value: str, icon: str = "", delta: str | None = None):
    """Render a styled metric card using st.metric (no raw HTML divs)."""
    display_label = f"{icon} {label}" if icon else label
    st.metric(label=display_label, value=value, delta=delta)


def aqi_badge(aqi: int):
    desc, color = get_aqi_description(aqi)
    level = "good" if aqi <= 50 else ("moderate" if aqi <= 100 else "poor")
    st.markdown(
        f"<span class='badge-{level}'>AQI {aqi} — {desc}</span>",
        unsafe_allow_html=True,
    )


def alert_box(alert: dict):
    css_cls = "alert-danger" if alert.get("level") == "danger" else "alert-warning"
    icon = "🔴" if alert.get("level") == "danger" else "🟡"
    st.markdown(
        f"""<div class='{css_cls}'>
            {icon} <strong>{alert['type'].replace('_',' ').title()}</strong> — {alert['message']}
            <br><small style='opacity:.6'>{alert.get('timestamp','')}</small>
        </div>""",
        unsafe_allow_html=True,
    )


def risk_gauge(title: str, probability: float) -> go.Figure:
    pct = probability * 100
    color = RISK_COLOR["high"] if pct >= 70 else (RISK_COLOR["medium"] if pct >= 40 else RISK_COLOR["low"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        title={"text": title, "font": {"color": "#94a3b8", "size": 13}},
        number={"suffix": "%", "font": {"color": color, "size": 22}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569"},
            "bar": {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "steps": [
                {"range": [0, 40],  "color": "rgba(16,185,129,0.15)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.15)"},
                {"range": [70, 100],"color": "rgba(239,68,68,0.15)"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.75, "value": pct},
        },
    ))
    layout = {k: v for k, v in PLOTLY_THEME.items() if k != "margin"}
    fig.update_layout(**layout, height=200, margin=dict(l=20, r=20, t=40, b=10))
    return fig


def section_header(text: str):
    st.markdown(f"<div class='section-header'>{text}</div>", unsafe_allow_html=True)
