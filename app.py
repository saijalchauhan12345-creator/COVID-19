import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Config
st.set_page_config(
    page_title="COVID Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Helper: blue HTML table ──
def blue_table(dataframe):
    fmt = dataframe.copy()
    for col in fmt.select_dtypes(include='number').columns:
        if "Rate" in col or "%" in col:
            fmt[col] = fmt[col].map(lambda x: f"{x:.2f}%")
        else:
            fmt[col] = fmt[col].map(lambda x: f"{x:,}")

    rows_html = ""
    for i, (_, row) in enumerate(fmt.iterrows()):
        bg = "rgba(5,20,60,0.95)" if i % 2 == 0 else "rgba(8,30,80,0.85)"
        cells = "".join(
            f"<td style='padding:10px 16px;color:#e0f2fe;"
            f"border-bottom:1px solid rgba(56,189,248,0.12);'>{v}</td>"
            for v in row
        )
        rows_html += f"<tr style='background:{bg};'>{cells}</tr>"

    headers = "".join(
        f"<th style='padding:11px 16px;text-align:left;"
        f"background:linear-gradient(90deg,rgba(14,116,144,.75),rgba(30,64,175,.65));"
        f"color:#bae6fd;font-weight:700;font-size:12px;letter-spacing:.5px;"
        f"text-transform:uppercase;border-bottom:2px solid rgba(56,189,248,.5);'>{c}</th>"
        for c in fmt.columns
    )

    st.markdown(f"""
    <div style="border-radius:14px;border:1px solid rgba(56,189,248,.35);
        box-shadow:0 0 22px rgba(14,165,233,.22),0 0 50px rgba(56,189,248,.08);
        overflow:hidden;margin-bottom:16px;">
    <table style="width:100%;border-collapse:collapse;font-size:13px;font-family:sans-serif;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>
    """, unsafe_allow_html=True)


# ── CSS ──
st.markdown("""
<style>

.stApp { background: #050816; color: white; }

/* Hide sidebar entirely */
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Full width main content — no left gap */
.stMainBlockContainer {
    max-width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* ── Filter Toggle Expander ── */
[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-bottom: 6px !important;
}

/* The clickable header row — looks like a button */
[data-testid="stExpander"] summary {
    background: linear-gradient(135deg, rgba(8,14,50,0.95), rgba(4,8,30,0.98)) !important;
    border: 1px solid rgba(56,189,248,.4) !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    color: #bae6fd !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: .6px !important;
    box-shadow: 0 0 14px rgba(14,165,233,.2), 0 0 30px rgba(56,189,248,.08) !important;
    transition: all .2s ease !important;
    display: inline-flex !important;
    width: auto !important;
    min-width: 220px !important;
}

[data-testid="stExpander"] summary:hover {
    background: linear-gradient(135deg, rgba(14,116,144,.5), rgba(30,64,175,.5)) !important;
    box-shadow: 0 0 22px rgba(14,165,233,.4), 0 0 50px rgba(56,189,248,.18) !important;
    color: #ffffff !important;
    border-color: rgba(56,189,248,.7) !important;
}

[data-testid="stExpander"] svg {
    color: #38bdf8 !important;
    stroke: #38bdf8 !important;
}

/* Expanded content area */
[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {
    background: linear-gradient(135deg, rgba(5,12,40,0.97), rgba(3,7,25,0.98)) !important;
    border: 1px solid rgba(56,189,248,.25) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 8px 24px rgba(14,165,233,.1) !important;
    margin-top: -2px !important;
}

/* ── Neon KPI Cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 22px 18px;
    border: 1px solid rgba(139,92,246,.45);
    box-shadow:
        0 0 18px rgba(124,58,237,.55),
        0 0 40px rgba(124,58,237,.25),
        inset 0 0 20px rgba(124,58,237,.08);
    transition: box-shadow .3s ease;
}

[data-testid="stMetric"]:hover {
    box-shadow:
        0 0 28px rgba(236,72,153,.7),
        0 0 60px rgba(124,58,237,.4),
        inset 0 0 30px rgba(124,58,237,.12);
}

[data-testid="stMetricValue"] > div {
    font-size: 28px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 8px rgba(167,139,250,.8));
}

[data-testid="stMetricLabel"] > div {
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: .5px;
    text-transform: uppercase;
}

h1 { letter-spacing: -2px; }

/* ── Chart popup / pop-out hover effect ── */
.chart-wrap {
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
}
.chart-wrap:hover {
    transform: translateY(-5px) !important;
    box-shadow:
        0 0 28px rgba(236,72,153,0.7),
        0 0 60px rgba(124,58,237,0.4),
        inset 0 0 30px rgba(124,58,237,0.12) !important;
}

/* ── Multiselect ── */
div[data-baseweb="select"] > div {
    background: rgba(5,12,40,0.95) !important;
    border: 1px solid rgba(56,189,248,.4) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 12px rgba(14,165,233,.15) !important;
    color: #e0f2fe !important;
}

div[data-baseweb="select"] span { color: #e0f2fe !important; }

div[data-baseweb="tag"] {
    background: linear-gradient(135deg, rgba(14,116,144,.6), rgba(30,64,175,.55)) !important;
    border: 1px solid rgba(56,189,248,.4) !important;
    border-radius: 6px !important;
    color: #bae6fd !important;
}

ul[data-baseweb="menu"] {
    background: rgba(5,12,40,0.98) !important;
    border: 1px solid rgba(56,189,248,.3) !important;
    border-radius: 10px !important;
}

ul[data-baseweb="menu"] li { color: #e0f2fe !important; background: transparent !important; }
ul[data-baseweb="menu"] li:hover { background: rgba(14,165,233,.18) !important; }

/* ── Download Button ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, rgba(14,116,144,.5), rgba(30,64,175,.5)) !important;
    color: #bae6fd !important;
    border: 1px solid rgba(56,189,248,.45) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 0 14px rgba(14,165,233,.25), 0 0 30px rgba(56,189,248,.1) !important;
    transition: all .25s ease !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, rgba(14,116,144,.75), rgba(30,64,175,.7)) !important;
    box-shadow: 0 0 22px rgba(14,165,233,.45), 0 0 50px rgba(56,189,248,.2) !important;
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# ── Load Data ──
df = pd.read_csv("covid_data.csv")
df["Recovery Rate"] = (df["Recovered"] / df["Confirmed"] * 100).round(2)
all_countries = list(df["Country"].unique())

# ── Header ──
st.markdown("""
<h1 style='text-align:center;font-size:55px;
background:linear-gradient(to right,#4F46E5,#EC4899);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
🦠 COVID Analytics Dashboard
</h1>
<p style='text-align:center;font-size:18px;color:#64748B;'>
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
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Dataset", "🏆 Rankings"])

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
        font_color='#ccccff',
        showlegend=False,
        height=420,
        margin=dict(l=20, r=20, t=40, b=40),
        yaxis=dict(
            gridcolor='rgba(129,140,248,0.15)',
            color='#818cf8',
            tickfont=dict(size=11),
            zerolinecolor='rgba(129,140,248,0.3)',
        ),
        xaxis=dict(color='#a5b4fc', tickfont=dict(size=13)),
        bargap=0.28,
        hoverlabel=dict(
            bgcolor='rgba(10,10,40,0.95)',
            bordercolor='rgba(129,140,248,0.8)',
            font=dict(color='white', size=13)
        ),
    )
    fig_bar.update_traces(marker_line_width=0, selector=dict(type="bar"))

    # Neon border inside chart
    fig_bar.add_shape(type="rect", xref="paper", yref="paper",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(color="rgba(129,140,248,0.3)", width=1),
        fillcolor="rgba(0,0,0,0)")

    st.markdown("""
    <div class="chart-wrap" style="
        border-radius:20px;
        border:1px solid rgba(139,92,246,0.45);
        box-shadow:
            0 0 20px rgba(124,58,237,0.55),
            0 0 45px rgba(124,58,237,0.25),
            inset 0 0 30px rgba(124,58,237,0.08);
        overflow:hidden;
        padding:6px;
        background: rgba(255,255,255,0.04);
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
        font_color='#ccccff',
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(font=dict(color='#c4c4ff', size=12), bgcolor='rgba(0,0,0,0)'),
        hoverlabel=dict(
            bgcolor='rgba(10,10,40,0.95)',
            bordercolor='rgba(244,114,182,0.8)',
            font=dict(color='white', size=13)
        ),
    )
    fig_pie.update_traces(
        textfont_color='white',
        textfont_size=13,
        pull=[0.07] * len(filtered_df),
        marker=dict(line=dict(color='#02041a', width=3)),
        rotation=45,
    )

    st.markdown("""
    <div class="chart-wrap" style="
        border-radius:20px;
        border:1px solid rgba(236,72,153,0.45);
        box-shadow:
            0 0 20px rgba(236,72,153,0.55),
            0 0 45px rgba(236,72,153,0.25),
            inset 0 0 30px rgba(236,72,153,0.08);
        overflow:hidden;
        padding:6px;
        background: rgba(255,255,255,0.04);
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

# ── Footer ──
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ by Saijal Chauhan</center>",
    unsafe_allow_html=True
)