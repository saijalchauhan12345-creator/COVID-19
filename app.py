import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# Page Config
st.set_page_config(
    page_title="COVID Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Theme State ──
if "theme" not in st.session_state:
    st.session_state.theme = "Dark Neon"

THEMES = {
    "Dark Neon": {
        "bg": "radial-gradient(circle at 20% 0%, #0a0f2e 0%, #050816 45%, #030510 100%)",
        "text": "#e2e8f0",
        "card_bg": "rgba(255,255,255,0.035)",
        "card_border": "rgba(139,92,246,.4)",
        "accent1": "#a78bfa",
        "accent2": "#f472b6",
        "table_header": "linear-gradient(90deg,rgba(14,116,144,.8),rgba(30,64,175,.7))",
        "table_text": "#bae6fd",
        "row_even": "rgba(6,16,52,0.92)",
        "row_odd": "rgba(10,26,70,0.82)",
        "muted": "#64748b",
        "map_ocean": "rgba(2,4,25,1)",
        "map_land": "rgba(20,20,45,0.6)",
        "map_coast": "rgba(129,140,248,0.3)",
        "map_wrap_bg": "rgba(255,255,255,0.04)",
        "hover_bg": "rgba(10,10,40,0.95)",
        "hover_text": "#ffffff",
    },
    "Light": {
        "bg": "radial-gradient(circle at 20% 0%, #f8fafc 0%, #eef2f7 45%, #e8ecf3 100%)",
        "text": "#1e293b",
        "card_bg": "rgba(255,255,255,0.85)",
        "card_border": "rgba(124,58,237,.25)",
        "accent1": "#7c3aed",
        "accent2": "#db2777",
        "table_header": "linear-gradient(90deg,rgba(186,230,253,.9),rgba(196,181,253,.8))",
        "table_text": "#1e293b",
        "row_even": "rgba(255,255,255,0.9)",
        "row_odd": "rgba(241,245,249,0.95)",
        "muted": "#64748b",
        "map_ocean": "rgba(219,234,254,0.6)",
        "map_land": "rgba(241,245,249,0.9)",
        "map_coast": "rgba(124,58,237,0.35)",
        "map_wrap_bg": "rgba(255,255,255,0.9)",
        "hover_bg": "rgba(255,255,255,0.98)",
        "hover_text": "#1e293b",
    },
    "Blue Only": {
        "bg": "radial-gradient(circle at 20% 0%, #061226 0%, #030a18 45%, #02060f 100%)",
        "text": "#dbeafe",
        "card_bg": "rgba(56,189,248,0.04)",
        "card_border": "rgba(56,189,248,.45)",
        "accent1": "#38bdf8",
        "accent2": "#0ea5e9",
        "table_header": "linear-gradient(90deg,rgba(14,116,144,.85),rgba(8,47,73,.85))",
        "table_text": "#bae6fd",
        "row_even": "rgba(4,18,46,0.92)",
        "row_odd": "rgba(7,30,75,0.85)",
        "muted": "#60a5fa",
        "map_ocean": "rgba(2,10,24,1)",
        "map_land": "rgba(10,30,55,0.6)",
        "map_coast": "rgba(56,189,248,0.35)",
        "map_wrap_bg": "rgba(56,189,248,0.04)",
        "hover_bg": "rgba(4,15,35,0.95)",
        "hover_text": "#dbeafe",
    },
}


T = THEMES[st.session_state.theme]

# ── Helper: themed HTML table ──
def blue_table(dataframe):
    fmt = dataframe.copy()
    for col in fmt.select_dtypes(include='number').columns:
        if "Rate" in col or "%" in col:
            fmt[col] = fmt[col].map(lambda x: f"{x:.2f}%")
        else:
            fmt[col] = fmt[col].map(lambda x: f"{x:,}")

    rows_html = ""
    for i, (_, row) in enumerate(fmt.iterrows()):
        bg = T["row_even"] if i % 2 == 0 else T["row_odd"]
        cells = "".join(
            f"<td style='padding:11px 18px;color:{T['text']};font-size:13.5px;"
            f"font-weight:500;border-bottom:1px solid rgba(56,189,248,0.1);"
            f"transition:background .15s ease;'>{v}</td>"
            for v in row
        )
        rows_html += (
            f"<tr style='background:{bg};' "
            f"onmouseover=\"this.style.background='rgba(14,165,233,0.16)'\" "
            f"onmouseout=\"this.style.background='{bg}'\">{cells}</tr>"
        )

    headers = "".join(
        f"<th style='padding:13px 18px;text-align:left;"
        f"background:{T['table_header']};"
        f"color:{T['table_text']};font-weight:700;font-size:11.5px;letter-spacing:.7px;"
        f"text-transform:uppercase;border-bottom:2px solid rgba(56,189,248,.55);'>{c}</th>"
        for c in fmt.columns
    )

    st.markdown(f"""
    <div style="border-radius:16px;border:1px solid rgba(56,189,248,.3);
        box-shadow:0 0 24px rgba(14,165,233,.18),0 0 55px rgba(56,189,248,.07);
        overflow:hidden;margin-bottom:18px;">
    <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>
    """, unsafe_allow_html=True)


# ── CSS ──
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Sora:wght@600;700;800&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

html, body, .stApp {
    background: #050816 !important;
    color: #e2e8f0;
    scroll-behavior: smooth;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: rgba(5,8,30,0.6); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(56,189,248,.5), rgba(139,92,246,.5));
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, rgba(56,189,248,.8), rgba(139,92,246,.8));
}

/* Hide sidebar entirely */
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Full width main content, tightened vertical rhythm */
.stMainBlockContainer {
    max-width: 100% !important;
    padding: 1.6rem 2.4rem 3rem 2.4rem !important;
}

.block-container { padding-top: 1.5rem !important; }

/* Section headers */
h1 {
    font-family: 'Sora', sans-serif !important;
    letter-spacing: -1.5px;
    font-weight: 800 !important;
}

h2, h3 {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -.3px !important;
    color: #f1f5f9 !important;
    margin-top: 0.4rem !important;
    margin-bottom: 0.8rem !important;
}

/* Streamlit subheader spacing tightened */
[data-testid="stMarkdownContainer"] h3 {
    font-size: 1.25rem !important;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(139,92,246,0.15);
}

/* Captions */
[data-testid="stCaptionContainer"] {
    color: #64748b !important;
    font-size: 12.5px !important;
    letter-spacing: .2px;
}

/* Divider */
hr {
    border-color: rgba(139,92,246,0.18) !important;
    margin: 1.2rem 0 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid rgba(56,189,248,0.15);
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px 10px 0 0 !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    padding: 10px 18px !important;
    transition: all .25s ease !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #bae6fd !important;
    background: rgba(56,189,248,0.06) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(180deg, rgba(124,58,237,0.18), rgba(56,189,248,0.06)) !important;
    box-shadow: inset 0 -3px 0 0 #a78bfa !important;
}

/* ── Filter Toggle Expander ── */
[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-bottom: 14px !important;
    max-width: 260px !important;
}

[data-testid="stExpander"] summary {
    background: linear-gradient(135deg, rgba(8,14,50,0.95), rgba(4,8,30,0.98)) !important;
    border: 1px solid rgba(56,189,248,.4) !important;
    border-radius: 12px !important;
    padding: 11px 22px !important;
    color: #bae6fd !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    letter-spacing: .6px !important;
    box-shadow: 0 0 14px rgba(14,165,233,.18), 0 0 30px rgba(56,189,248,.06) !important;
    transition: all .25s cubic-bezier(.4,0,.2,1) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
    width: auto !important;
    min-width: 200px !important;
    white-space: nowrap !important;
    position: relative !important;
}

[data-testid="stExpander"] summary span {
    white-space: nowrap !important;
    overflow: visible !important;
}

/* Hide broken material-icon fallback text (renders as literal icon name) */
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] summary .material-icons,
[data-testid="stExpander"] summary span[class*="icon"] {
    font-size: 0 !important;
    line-height: 0 !important;
    color: transparent !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    margin-left: 4px !important;
    position: relative !important;
    display: inline-block !important;
}

/* Draw a clean custom chevron instead */
[data-testid="stExpander"] summary svg::after,
[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::after {
    content: "▾" !important;
    font-size: 14px !important;
    line-height: 14px !important;
    color: #38bdf8 !important;
    position: absolute !important;
    left: 0; top: 1px;
}

/* Catch-all: any stray text node after the label that isn't our own span */
[data-testid="stExpander"] summary > *:not(:first-child):not(svg):not([data-testid="stIconMaterial"]) {
    font-size: 0 !important;
}

[data-testid="stExpander"] summary:hover {
    background: linear-gradient(135deg, rgba(14,116,144,.55), rgba(30,64,175,.5)) !important;
    box-shadow: 0 0 24px rgba(14,165,233,.4), 0 0 55px rgba(56,189,248,.2) !important;
    color: #ffffff !important;
    border-color: rgba(56,189,248,.75) !important;
    transform: translateY(-1px);
}

[data-testid="stExpander"] svg {
    color: #38bdf8 !important;
    stroke: #38bdf8 !important;
}

[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {
    background: linear-gradient(135deg, rgba(5,12,40,0.97), rgba(3,7,25,0.98)) !important;
    border: 1px solid rgba(56,189,248,.25) !important;
    border-top: none !important;
    border-radius: 0 0 14px 14px !important;
    padding: 18px 22px !important;
    box-shadow: 0 10px 28px rgba(14,165,233,.1) !important;
    margin-top: -2px !important;
}

/* ── Neon KPI Cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.035);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: 18px;
    padding: 20px 20px 18px 20px;
    border: 1px solid rgba(139,92,246,.4);
    box-shadow:
        0 0 18px rgba(124,58,237,.5),
        0 0 38px rgba(124,58,237,.22),
        inset 0 0 22px rgba(124,58,237,.07);
    transition: all .3s cubic-bezier(.4,0,.2,1);
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: rgba(236,72,153,.55);
    box-shadow:
        0 8px 12px rgba(0,0,0,.25),
        0 0 30px rgba(236,72,153,.65),
        0 0 65px rgba(124,58,237,.4),
        inset 0 0 30px rgba(124,58,237,.1);
}

[data-testid="stMetricValue"] > div {
    font-family: 'Sora', sans-serif !important;
    font-size: 27px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 10px rgba(167,139,250,.7));
    line-height: 1.2 !important;
}

[data-testid="stMetricLabel"] > div {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: .8px;
    text-transform: uppercase;
}

[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stMetricDelta"] {
    font-weight: 600 !important;
    font-size: 12.5px !important;
}

/* ── Chart pop-out hover effect, refined ── */
.chart-wrap {
    transition: transform .35s cubic-bezier(.4,0,.2,1), box-shadow .35s cubic-bezier(.4,0,.2,1) !important;
}
.chart-wrap:hover {
    transform: translateY(-6px) !important;
    box-shadow:
        0 14px 18px rgba(0,0,0,.3),
        0 0 32px rgba(236,72,153,0.6),
        0 0 65px rgba(124,58,237,0.35),
        inset 0 0 30px rgba(124,58,237,0.1) !important;
}

/* ── Multiselect ── */
div[data-baseweb="select"] > div {
    background: rgba(5,12,40,0.95) !important;
    border: 1px solid rgba(56,189,248,.4) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 12px rgba(14,165,233,.12) !important;
    color: #e0f2fe !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: rgba(56,189,248,.7) !important;
    box-shadow: 0 0 18px rgba(14,165,233,.22) !important;
}

div[data-baseweb="select"] span { color: #e0f2fe !important; }

div[data-baseweb="tag"] {
    background: linear-gradient(135deg, rgba(14,116,144,.6), rgba(30,64,175,.55)) !important;
    border: 1px solid rgba(56,189,248,.4) !important;
    border-radius: 6px !important;
    color: #bae6fd !important;
    font-weight: 600 !important;
    font-size: 12.5px !important;
}

ul[data-baseweb="menu"] {
    background: rgba(5,12,40,0.98) !important;
    border: 1px solid rgba(56,189,248,.3) !important;
    border-radius: 10px !important;
}

ul[data-baseweb="menu"] li { color: #e0f2fe !important; background: transparent !important; }
ul[data-baseweb="menu"] li:hover { background: rgba(14,165,233,.18) !important; }

/* ── Text inputs / Selectboxes (general) ── */
.stTextInput > div > div,
.stSelectbox > div > div {
    background: rgba(5,12,40,0.9) !important;
    border: 1px solid rgba(56,189,248,.3) !important;
    border-radius: 10px !important;
    color: #e0f2fe !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}

.stTextInput > div > div:focus-within,
.stSelectbox > div > div:focus-within {
    border-color: rgba(56,189,248,.8) !important;
    box-shadow: 0 0 14px rgba(14,165,233,.3) !important;
}

.stTextInput input { color: #e0f2fe !important; }

label, .stTextInput label, .stSelectbox label {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* ── Buttons (generic) ── */
.stButton button {
    background: linear-gradient(135deg, rgba(14,116,144,.5), rgba(30,64,175,.5)) !important;
    color: #bae6fd !important;
    border: 1px solid rgba(56,189,248,.45) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: .3px;
    box-shadow: 0 0 14px rgba(14,165,233,.22), 0 0 30px rgba(56,189,248,.08) !important;
    transition: all .25s cubic-bezier(.4,0,.2,1) !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, rgba(14,116,144,.75), rgba(30,64,175,.7)) !important;
    box-shadow: 0 0 22px rgba(14,165,233,.45), 0 0 50px rgba(56,189,248,.2) !important;
    color: #ffffff !important;
    transform: translateY(-2px);
}

.stButton button:active { transform: translateY(0px); }

/* ── Download Button ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, rgba(14,116,144,.5), rgba(30,64,175,.5)) !important;
    color: #bae6fd !important;
    border: 1px solid rgba(56,189,248,.45) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: .3px;
    box-shadow: 0 0 14px rgba(14,165,233,.22), 0 0 30px rgba(56,189,248,.08) !important;
    transition: all .25s cubic-bezier(.4,0,.2,1) !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, rgba(14,116,144,.75), rgba(30,64,175,.7)) !important;
    box-shadow: 0 0 22px rgba(14,165,233,.45), 0 0 50px rgba(56,189,248,.2) !important;
    color: #ffffff !important;
    transform: translateY(-2px);
}

/* ── Alert boxes (info/success/warning/error) ── */
[data-testid="stAlertContainer"] {
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
    font-size: 14px !important;
    font-weight: 500 !important;
    border-width: 1px !important;
    border-style: solid !important;
}

div[data-testid="stAlertContainer"][class*="info"],
.stAlert p { color: #e2e8f0 !important; }

/* Progress bars */
.stProgress > div > div {
    background: linear-gradient(90deg, #818cf8, #f472b6) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(129,140,248,.5) !important;
}
.stProgress > div { background: rgba(255,255,255,0.06) !important; border-radius: 8px !important; }

/* Spinner */
.stSpinner > div {
    border-top-color: #38bdf8 !important;
}

</style>
""", unsafe_allow_html=True)

# ── Theme-specific override (background, text, accent colors) ──
st.markdown(f"""
<style>
html, body, .stApp {{
    background: {T['bg']} !important;
    color: {T['text']} !important;
}}

[data-testid="stMetric"] {{
    background: {T['card_bg']} !important;
    border-color: {T['card_border']} !important;
}}

h1, h2, h3, p, span, label, .stMarkdown {{
    color: {T['text']} !important;
}}

[data-testid="stCaptionContainer"] {{
    color: {T['muted']} !important;
}}

/* ── Filter expander button (Filters toggle) ── */
[data-testid="stExpander"] summary {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['card_border']} !important;
    color: {T['text']} !important;
}}

[data-testid="stExpander"] summary:hover {{
    color: {T['accent1']} !important;
    border-color: {T['accent1']} !important;
}}

[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['card_border']} !important;
}}

[data-testid="stExpander"] summary svg::after,
[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::after {{
    color: {T['accent1']} !important;
}}

/* ── Multiselect / Selectbox / Text input ── */
div[data-baseweb="select"] > div {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['card_border']} !important;
    color: {T['text']} !important;
}}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div {{
    color: {T['text']} !important;
}}

div[data-baseweb="tag"] {{
    background: {T['table_header']} !important;
    border: 1px solid {T['card_border']} !important;
    color: {T['table_text']} !important;
}}

div[data-baseweb="tag"] span {{
    color: {T['table_text']} !important;
}}

ul[data-baseweb="menu"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['card_border']} !important;
}}

ul[data-baseweb="menu"] li {{
    color: {T['text']} !important;
}}

.stTextInput > div > div,
.stSelectbox > div > div {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['card_border']} !important;
}}

.stTextInput input {{ color: {T['text']} !important; }}

label, .stTextInput label, .stSelectbox label {{
    color: {T['muted']} !important;
}}

/* ── Buttons ── */
.stButton button,
[data-testid="stDownloadButton"] button {{
    background: {T['card_bg']} !important;
    color: {T['text']} !important;
    border: 1px solid {T['card_border']} !important;
}}

.stButton button:hover,
[data-testid="stDownloadButton"] button:hover {{
    color: {T['accent1']} !important;
    border-color: {T['accent1']} !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab"] {{
    color: {T['muted']} !important;
}}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {{
    color: {T['accent1']} !important;
}}

[data-testid="stTabs"] [aria-selected="true"] {{
    color: {T['text']} !important;
}}

/* ── Alerts (info/success/warning/error) ── */
[data-testid="stAlertContainer"] p,
[data-testid="stAlertContainer"] span {{
    color: {T['text']} !important;
}}

/* ── Theme Toggle Buttons ── */
.stButton button[kind="secondary"] {{
    background: {T['card_bg']} !important;
    color: {T['muted']} !important;
    border: 1px solid {T['card_border']} !important;
    font-weight: 600 !important;
}}

.stButton button[kind="secondary"]:hover {{
    color: {T['accent1']} !important;
    border-color: {T['accent1']} !important;
}}

.stButton button[kind="primary"] {{
    background: linear-gradient(135deg, {T['accent1']}, {T['accent2']}) !important;
    color: #ffffff !important;
    border: 1px solid {T['accent1']} !important;
    font-weight: 700 !important;
    box-shadow: 0 0 16px {T['accent1']}55 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Load Data ──
df = pd.read_csv("covid_data.csv")
df["Recovery Rate"] = (df["Recovered"] / df["Confirmed"] * 100).round(2)
all_countries = list(df["Country"].unique())

# ── Theme Toggle (button row) ──
theme_left, theme_right = st.columns([3, 2])
with theme_right:
    tbtn1, tbtn2, tbtn3 = st.columns(3)
    theme_buttons = {
        "Dark Neon": (tbtn1, "🌑 Dark"),
        "Light": (tbtn2, "☀️ Light"),
        "Blue Only": (tbtn3, "🔵 Blue"),
    }
    for theme_name, (col, label) in theme_buttons.items():
        with col:
            is_active = st.session_state.theme == theme_name
            if st.button(
                label,
                key=f"theme_btn_{theme_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                if not is_active:
                    st.session_state.theme = theme_name
                    st.rerun()

# ── Header ──
st.markdown("""
<h1 style='text-align:center;font-size:52px;margin-bottom:0;
font-family:"Sora",sans-serif;font-weight:800;
background:linear-gradient(100deg,#4F46E5,#a78bfa,#EC4899);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;
filter:drop-shadow(0 0 18px rgba(124,58,237,0.35));'>
🦠 COVID Analytics Dashboard
</h1>
<p style='text-align:center;font-size:15.5px;color:#64748B;
letter-spacing:.4px;margin-top:6px;font-weight:500;'>
Interactive Analytics using Streamlit
</p>
""", unsafe_allow_html=True)

st.divider()

# ── Filter Toggle — left aligned ──
left_col, _ = st.columns([1, 3])
with left_col:
    with st.expander("☰  Filters", expanded=False):
        st.markdown("""
        <p style="color:#94a3b8;font-size:12px;font-weight:600;letter-spacing:.5px;
        text-transform:uppercase;margin-bottom:6px;">🌍 Select Countries</p>
        """, unsafe_allow_html=True)

        selected_countries = st.multiselect(
            label="Countries",
            options=all_countries,
            default=all_countries,
            label_visibility="collapsed"
        )

if not selected_countries:
    selected_countries = all_countries

filtered_df = df[df["Country"].isin(selected_countries)]

# ── KPI Cards ──
st.subheader("📌 Key Metrics")

recovery_rate = (
    (filtered_df["Recovered"].sum() / filtered_df["Confirmed"].sum()) * 100
) if filtered_df["Confirmed"].sum() > 0 else 0

death_rate = (
    (filtered_df["Deaths"].sum() / filtered_df["Confirmed"].sum()) * 100
) if filtered_df["Confirmed"].sum() > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🦠 Cases",      f"{filtered_df['Confirmed'].sum():,}")
col2.metric("💀 Deaths",     f"{filtered_df['Deaths'].sum():,}")
col3.metric("💚 Recovered",  f"{filtered_df['Recovered'].sum():,}")
col4.metric("📈 Recovery %", f"{recovery_rate:.2f}%")
col5.metric("📉 Death %",    f"{death_rate:.2f}%")

# ── Tabs ──
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Dashboard", "📋 Dataset", "🏆 Rankings", "🔮 Prediction", "🗺️ World Map"]
)

# ════════════════════════════════════════
# TAB 1 — Dashboard
# ════════════════════════════════════════
with tab1:

    st.subheader("📊 Confirmed Cases")

    neon_colors = ['#818cf8','#c084fc','#f472b6','#fbbf24','#34d399',
                   '#60a5fa','#fb923c','#a3e635','#e879f9','#2dd4bf']

    fig_bar = go.Figure()
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        color = neon_colors[idx % len(neon_colors)]
        fig_bar.add_trace(go.Bar(
            x=[row['Country']], y=[row['Confirmed']], name=row['Country'],
            marker=dict(
                color=color,
                opacity=0.9,
                line=dict(color=color, width=2),
            ),
            hovertemplate=f"<b>{row['Country']}</b><br>Confirmed: {row['Confirmed']:,}<extra></extra>"
        ))

    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=T["text"],
        showlegend=False,
        height=420,
        margin=dict(l=20, r=20, t=40, b=40),
        yaxis=dict(
            gridcolor='rgba(129,140,248,0.15)',
            color=T["muted"],
            tickfont=dict(size=11),
            zerolinecolor='rgba(129,140,248,0.3)',
        ),
        xaxis=dict(color=T["muted"], tickfont=dict(size=13)),
        bargap=0.28,
        hoverlabel=dict(
            bgcolor=T["hover_bg"],
            bordercolor=T["card_border"],
            font=dict(color=T["hover_text"], size=13)
        ),
    )
    fig_bar.update_traces(marker_line_width=0, selector=dict(type="bar"))

    # Neon border inside chart
    fig_bar.add_shape(type="rect", xref="paper", yref="paper",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(color="rgba(129,140,248,0.3)", width=1),
        fillcolor="rgba(0,0,0,0)")

    st.markdown(f"""
    <div class="chart-wrap" style="
        border-radius:20px;
        border:1px solid {T['card_border']};
        box-shadow:
            0 0 20px rgba(124,58,237,0.4),
            0 0 45px rgba(124,58,237,0.18),
            inset 0 0 30px rgba(124,58,237,0.06);
        overflow:hidden;
        padding:6px;
        background: {T['map_wrap_bg']};
        backdrop-filter: blur(12px);
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    ">
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🥧 Cases Distribution")

    fig_pie = px.pie(
        filtered_df, names='Country', values='Confirmed', hole=0.42,
        color_discrete_sequence=['#818cf8','#f472b6','#34d399','#fbbf24','#c084fc',
                                  '#60a5fa','#fb923c','#a3e635','#e879f9','#2dd4bf'],
        height=460
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=T["text"],
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(font=dict(color=T["text"], size=12), bgcolor='rgba(0,0,0,0)'),
        hoverlabel=dict(
            bgcolor=T["hover_bg"],
            bordercolor=T["card_border"],
            font=dict(color=T["hover_text"], size=13)
        ),
    )
    fig_pie.update_traces(
        textfont_color='white' if st.session_state.theme != "Light" else '#1e293b',
        textfont_size=13,
        pull=[0.07] * len(filtered_df),
        marker=dict(line=dict(color=T["map_ocean"], width=3)),
        rotation=45,
    )

    st.markdown(f"""
    <div class="chart-wrap" style="
        border-radius:20px;
        border:1px solid {T['card_border']};
        box-shadow:
            0 0 20px rgba(236,72,153,0.4),
            0 0 45px rgba(236,72,153,0.18),
            inset 0 0 30px rgba(236,72,153,0.06);
        overflow:hidden;
        padding:6px;
        background: {T['map_wrap_bg']};
        backdrop-filter: blur(12px);
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    ">
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not filtered_df.empty:
        highest = filtered_df.loc[filtered_df["Confirmed"].idxmax(), "Country"]
        lowest  = filtered_df.loc[filtered_df["Confirmed"].idxmin(), "Country"]
        st.info(f"🏆 Highest Cases: **{highest}** | 🌱 Lowest Cases: **{lowest}**")

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ════════════════════════════════════
    # 🌦️ Live Weather Lookup
    # ════════════════════════════════════
    st.subheader("🌦️ Live Weather Lookup")
    st.caption("Enter a country and city to get current weather conditions.")

    wcol1, wcol2, wcol3 = st.columns([2, 2, 1])
    with wcol1:
        weather_country = st.text_input("Country", placeholder="e.g. India", key="weather_country")
    with wcol2:
        weather_city = st.text_input("City", placeholder="e.g. Noida", key="weather_city")
    with wcol3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        fetch_weather = st.button("🔍 Get Weather", use_container_width=True)

    if fetch_weather and weather_city:
        query = f"{weather_city}, {weather_country}" if weather_country else weather_city
        try:
            geo_resp = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": weather_city, "count": 5, "language": "en", "format": "json"},
                timeout=10
            ).json()

            results = geo_resp.get("results", [])
            # If country given, try to match it among results
            match = None
            if weather_country:
                for r in results:
                    if weather_country.strip().lower() in r.get("country", "").lower():
                        match = r
                        break
            if not match and results:
                match = results[0]

            if not match:
                st.warning(f"⚠️ Couldn't find weather data for '{query}'. Try a different spelling.")
            else:
                lat, lon = match["latitude"], match["longitude"]
                found_city = match["name"]
                found_country = match.get("country", "")

                wx_resp = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat, "longitude": lon,
                        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                        "timezone": "auto"
                    },
                    timeout=10
                ).json()

                current = wx_resp.get("current", {})
                temp = current.get("temperature_2m")
                humidity = current.get("relative_humidity_2m")
                wind = current.get("wind_speed_10m")
                code = current.get("weather_code")

                weather_icons = {
                    0: "☀️ Clear sky", 1: "🌤️ Mainly clear", 2: "⛅ Partly cloudy",
                    3: "☁️ Overcast", 45: "🌫️ Fog", 48: "🌫️ Fog",
                    51: "🌦️ Light drizzle", 61: "🌧️ Rain", 63: "🌧️ Moderate rain",
                    65: "🌧️ Heavy rain", 71: "🌨️ Snow", 80: "🌦️ Rain showers",
                    95: "⛈️ Thunderstorm",
                }
                condition = weather_icons.get(code, "🌡️ Unknown")

                st.success(f"📍 Weather in **{found_city}, {found_country}**")

                wm1, wm2, wm3, wm4 = st.columns(4)
                wm1.metric("🌡️ Temperature", f"{temp}°C" if temp is not None else "N/A")
                wm2.metric("💧 Humidity", f"{humidity}%" if humidity is not None else "N/A")
                wm3.metric("💨 Wind Speed", f"{wind} km/h" if wind is not None else "N/A")
                wm4.metric("☁️ Condition", condition)

        except Exception as e:
            st.error(f"⚠️ Could not fetch weather data right now. Please try again.")
    elif fetch_weather and not weather_city:
        st.warning("⚠️ Please enter a city name.")


# ════════════════════════════════════════
# TAB 2 — Dataset
# ════════════════════════════════════════
with tab2:

    st.download_button(
        label="📥 Download Dataset",
        data=filtered_df.to_csv(index=False),
        file_name="covid_data.csv",
        mime="text/csv"
    )

    st.subheader("📋 Dataset")
    blue_table(filtered_df.reset_index(drop=True))

    search = st.text_input("🔍 Search Country")
    if search:
        result = df[df["Country"].str.contains(search.strip(), case=False, na=False)]
        if not result.empty:
            st.success(f"✅ Found {len(result)} result(s) for **'{search}'**")
            blue_table(result.reset_index(drop=True))
        else:
            st.warning(f"⚠️ No country found matching **'{search}'**")

    st.subheader("📈 Trend Analysis")
    avg_cases = filtered_df["Confirmed"].mean()
    st.info(f"📈 Average Confirmed Cases: {avg_cases:,.0f}")

# ════════════════════════════════════════
# TAB 3 — Rankings
# ════════════════════════════════════════
with tab3:

    st.success("🥇 Top Performing Countries (by Cases)")
    top3 = filtered_df.sort_values(by="Confirmed", ascending=False).head(3)
    for i, row in top3.iterrows():
        st.success(f"🏆 {row['Country']} — {row['Confirmed']:,} cases")

    st.subheader("💚 Recovery Rate Ranking")
    ranking = (
        filtered_df[["Country", "Recovery Rate"]]
        .sort_values("Recovery Rate", ascending=False)
        .reset_index(drop=True)
    )
    blue_table(ranking)

    st.subheader("⚔️ Country Comparison")
    comparison = filtered_df[[
        "Country", "Confirmed", "Deaths", "Recovered", "Recovery Rate"
    ]].sort_values("Confirmed", ascending=False).reset_index(drop=True)
    blue_table(comparison)

    st.subheader("🏅 Country Progress")
    max_cases = filtered_df["Confirmed"].max()
    for _, row in filtered_df.iterrows():
        st.write(f"🌍 **{row['Country']}** — {row['Confirmed']:,}")
        st.progress(int((row["Confirmed"] / max_cases) * 100))

# ════════════════════════════════════════
# TAB 4 — Prediction (real data)
# ════════════════════════════════════════
with tab4:

    st.subheader("🔮 COVID Trend Prediction")
    st.caption(
        "Real historical data fetched live from the disease.sh public API "
        "(sourced from Johns Hopkins University CSSE), with a linear-regression "
        "forecast for the next 14 days."
    )

    pred_col1, pred_col2 = st.columns([2, 1])
    with pred_col1:
        pred_country = st.selectbox(
            "Select a country to forecast",
            options=all_countries,
            key="pred_country"
        )
    with pred_col2:
        lookback_days = st.selectbox(
            "Historical window",
            options=[30, 60, 90, 120],
            index=1,
            key="pred_lookback"
        )

    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_historical(country_name, days):
        url = f"https://disease.sh/v3/covid-19/historical/{country_name}"
        resp = requests.get(url, params={"lastdays": days}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        timeline = data.get("timeline", data)  # some responses nest under 'timeline'
        cases = timeline.get("cases", {})
        if not cases:
            return None
        s = pd.Series(cases)
        s.index = pd.to_datetime(s.index, format="%m/%d/%y")
        s = s.sort_index()
        return s

    if pred_country:
        with st.spinner(f"Fetching real COVID-19 history for {pred_country}..."):
            try:
                series = fetch_historical(pred_country, lookback_days)
            except Exception:
                series = None

        if series is None or series.empty:
            st.warning(
                f"⚠️ No historical data available for **{pred_country}** from the live API. "
                f"Try a different country name (disease.sh uses official country names)."
            )
        else:
            hist_df = pd.DataFrame({"Date": series.index, "Confirmed": series.values})

            # ── Linear regression forecast (14 days ahead) ──
            x = np.arange(len(hist_df))
            y = hist_df["Confirmed"].values.astype(float)
            slope, intercept = np.polyfit(x, y, 1)

            days_future = 14
            x_future = np.arange(len(hist_df), len(hist_df) + days_future)
            y_future = np.maximum(slope * x_future + intercept, y[-1])  # never predict below latest
            dates_future = pd.date_range(
                start=hist_df["Date"].iloc[-1] + timedelta(days=1), periods=days_future
            )

            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=hist_df["Date"], y=hist_df["Confirmed"],
                mode="lines", name="Historical (real data)",
                line=dict(color="#60a5fa", width=2.5),
                fill="tozeroy", fillcolor="rgba(96,165,250,0.08)"
            ))
            fig_pred.add_trace(go.Scatter(
                x=dates_future, y=y_future,
                mode="lines", name="Forecast (next 14 days)",
                line=dict(color="#f472b6", width=2.5, dash="dash"),
            ))

            fig_pred.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color=T["text"],
                height=420,
                margin=dict(l=20, r=20, t=30, b=40),
                yaxis=dict(gridcolor='rgba(129,140,248,0.15)', color=T["muted"],
                           title="Confirmed Cases"),
                xaxis=dict(color=T["muted"]),
                legend=dict(font=dict(color=T["text"], size=12),
                            bgcolor='rgba(0,0,0,0)', orientation="h", y=1.1),
                hoverlabel=dict(bgcolor=T["hover_bg"],
                                 bordercolor=T["card_border"],
                                 font=dict(color=T["hover_text"], size=12)),
            )

            st.markdown(f"""
            <div class="chart-wrap" style="
                border-radius:20px;
                border:1px solid {T['card_border']};
                box-shadow:0 0 20px rgba(244,114,182,0.35),0 0 45px rgba(244,114,182,0.15),
                    inset 0 0 30px rgba(244,114,182,0.05);
                overflow:hidden;padding:6px;background:{T['map_wrap_bg']};
                backdrop-filter:blur(12px);">
            """, unsafe_allow_html=True)
            st.plotly_chart(fig_pred, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            current_total = int(y[-1])
            end_forecast = int(y_future[-1])
            change = end_forecast - current_total

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Latest Confirmed", f"{current_total:,}")
            col_b.metric("Predicted in 14 days", f"{end_forecast:,}", delta=f"+{change:,}")
            avg_daily = (y[-1] - y[0]) / max(len(y) - 1, 1)
            col_c.metric("Avg. Daily New Cases", f"{avg_daily:,.0f}")

            st.caption(
                "📡 Data source: disease.sh (Johns Hopkins University CSSE). "
                "Forecast is a simple linear trend — actual future cases depend on many "
                "real-world factors not captured by this model."
            )

# ════════════════════════════════════════
# TAB 5 — World Map (Choropleth)
# ════════════════════════════════════════
with tab5:

    st.subheader("🗺️ Global Cases — Choropleth Map")
    st.caption("Countries shaded by confirmed case count. Hover for details.")

    map_metric = st.selectbox(
        "Color countries by",
        options=["Confirmed", "Deaths", "Recovered", "Recovery Rate"],
        index=0,
        key="map_metric"
    )

    color_scales = {
        "Confirmed": "Purples",
        "Deaths": "Reds",
        "Recovered": "Greens",
        "Recovery Rate": "Blues",
    }

    fig_map = px.choropleth(
        filtered_df,
        locations="Country",
        locationmode="country names",
        color=map_metric,
        hover_name="Country",
        hover_data={
            "Confirmed": ":,",
            "Deaths": ":,",
            "Recovered": ":,",
            "Recovery Rate": ":.2f",
        },
        color_continuous_scale=color_scales.get(map_metric, "Purples"),
        projection="natural earth",
    )

    fig_map.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=T["text"],
        height=520,
        margin=dict(l=10, r=10, t=20, b=10),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            lakecolor=T["map_ocean"],
            landcolor=T["map_land"],
            showframe=False,
            showcoastlines=True,
            coastlinecolor=T["map_coast"],
            showocean=True,
            oceancolor=T["map_ocean"],
        ),
        coloraxis_colorbar=dict(
            title=dict(text=map_metric, font=dict(color=T["text"])),
            tickfont=dict(color=T["text"]),
        ),
        hoverlabel=dict(
            bgcolor=T["hover_bg"],
            bordercolor=T["card_border"],
            font=dict(color=T["hover_text"], size=12)
        ),
    )

    st.markdown(f"""
    <div class="chart-wrap" style="
        border-radius:20px;
        border:1px solid {T['card_border']};
        box-shadow:0 0 20px rgba(124,58,237,0.25),0 0 45px rgba(124,58,237,0.1),
            inset 0 0 30px rgba(124,58,237,0.04);
        overflow:hidden;padding:6px;background:{T['map_wrap_bg']};
        backdrop-filter:blur(12px);">
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not filtered_df.empty:
        top_map = filtered_df.loc[filtered_df[map_metric].idxmax(), "Country"]
        st.info(f"🌍 Highest **{map_metric}**: **{top_map}**")

# ── Footer ──
st.markdown("---")
st.markdown(
    "<center style='color:#64748b;font-size:13px;font-weight:500;"
    "letter-spacing:.3px;padding-bottom:8px;'>Made with ❤️ by Saijal Chauhan</center>",
    unsafe_allow_html=True
)