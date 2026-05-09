"""ui_styles.py — Centralized dark-theme CSS for the dashboard."""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, body, .stApp { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%); color: #e2e8f0; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(13,27,42,0.95) !important;
    border-right: 1px solid rgba(0,212,255,0.15) !important;
    backdrop-filter: blur(12px);
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* Native st.metric cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px;
    padding: 1.2rem 1rem 1rem;
    backdrop-filter: blur(8px);
    transition: transform .2s, box-shadow .2s;
    margin-bottom: .4rem;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,212,255,0.12);
}
[data-testid="stMetricLabel"] {
    font-size: .78rem !important;
    color: #94a3b8 !important;
    letter-spacing: .06em;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #00d4ff !important;
}
[data-testid="stMetricDelta"] {
    font-size: .82rem !important;
    color: #64748b !important;
}

/* Hero header */
.hero-header {
    text-align: center;
    padding: 1.2rem 0 .6rem;
    background: linear-gradient(90deg, #00d4ff, #7c3aed, #00d4ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.6rem;
    font-weight: 800;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer { to { background-position: 200% center; } }

.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #00d4ff;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin: 1.2rem 0 .6rem;
    padding-bottom: .3rem;
    border-bottom: 1px solid rgba(0,212,255,0.25);
}

/* Alert boxes */
.alert-warning {
    background: rgba(245,158,11,0.12);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: .85rem 1rem;
    margin-bottom: .6rem;
    color: #fcd34d;
}
.alert-danger {
    background: rgba(239,68,68,0.12);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: .85rem 1rem;
    margin-bottom: .6rem;
    color: #fca5a5;
}
.alert-info {
    background: rgba(0,212,255,0.08);
    border-left: 4px solid #00d4ff;
    border-radius: 8px;
    padding: .85rem 1rem;
    margin-bottom: .6rem;
    color: #bae6fd;
}

/* Status badge */
.badge-good    { background: rgba(16,185,129,0.2); color: #6ee7b7; border: 1px solid #10b981; border-radius: 20px; padding: 2px 12px; font-size:.8rem; }
.badge-moderate{ background: rgba(245,158,11,0.2); color: #fcd34d; border: 1px solid #f59e0b; border-radius: 20px; padding: 2px 12px; font-size:.8rem; }
.badge-poor    { background: rgba(239,68,68,0.2);  color: #fca5a5; border: 1px solid #ef4444;  border-radius: 20px; padding: 2px 12px; font-size:.8rem; }

/* Plotly chart backgrounds */
.stPlotlyChart { border-radius: 12px; overflow: hidden; border: 1px solid rgba(0,212,255,0.1); }

/* Tabs */
[data-testid="stTabs"] button {
    color: #94a3b8 !important;
    font-weight: 500;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
    background: rgba(0,212,255,0.07) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid rgba(0,212,255,0.1); }

/* Footer */
.footer { text-align: center; color: #475569; font-size:.78rem; padding: 1rem 0; border-top: 1px solid rgba(0,212,255,0.1); margin-top: 2rem; }
</style>
"""

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)"),
    margin=dict(l=40, r=20, t=50, b=40),
)

AQI_COLORS = {
    "Good":                       "#10b981",
    "Moderate":                   "#f59e0b",
    "Unhealthy for Sensitive":    "#f97316",
    "Unhealthy":                  "#ef4444",
    "Very Unhealthy":             "#8b5cf6",
    "Hazardous":                  "#991b1b",
}

RISK_COLOR = {
    "low":    "#10b981",
    "medium": "#f59e0b",
    "high":   "#ef4444",
}
