import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Config
st.set_page_config(
    page_title="COVID Analytics Dashboard",
    page_icon="🦠",
    layout="wide"
)

# ── Helper: render any dataframe as a uniform blue HTML table ──
def blue_table(dataframe):
    """Renders a DataFrame as a styled HTML table with uniform blue rows."""
    fmt = dataframe.copy()
    # Format numeric columns nicely
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

    table_html = f"""
    <div style="
        border-radius:14px;
        border:1px solid rgba(56,189,248,.35);
        box-shadow:0 0 22px rgba(14,165,233,.22),0 0 50px rgba(56,189,248,.08);
        overflow:hidden;
        margin-bottom:16px;
    ">
    <table style="width:100%;border-collapse:collapse;font-size:13px;font-family:sans-serif;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# Custom CSS
st.markdown("""
<style>

.stApp {
    background: #050816;
    color: white;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f3d, #090b2f);
    border-right: 1px solid rgba(255,255,255,.1);
}

section[data-testid="stSidebar"] * { color: white; }

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

</style>
""", unsafe_allow_html=True)

# ── Load Data ──
df = pd.read_csv("covid_data.csv")
df["Recovery Rate"] = (df["Recovered"] / df["Confirmed"] * 100).round(2)

# ── Header ──
st.markdown("""
<h1 style='text-align:center;
font-size:55px;
background:linear-gradient(to right,#4F46E5,#EC4899);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
🦠 COVID Analytics Dashboard
</h1>
<p style='text-align:center; font-size:18px; color:#64748B;'>
Interactive Analytics using Streamlit
</p>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar ──
st.sidebar.header("⚙️ Filters")
st.sidebar.markdown("# 🌎 FILTERS\nSelect Countries")

selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    df["Country"].unique(),
    default=df["Country"].unique()
)

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

    neon_colors = ['#818cf8', '#c084fc', '#f472b6', '#fbbf24', '#34d399',
                   '#60a5fa', '#fb923c', '#a3e635', '#e879f9', '#2dd4bf']

    fig_bar = go.Figure()
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        color = neon_colors[idx % len(neon_colors)]
        fig_bar.add_trace(go.Bar(
            x=[row['Country']],
            y=[row['Confirmed']],
            name=row['Country'],
            marker=dict(color=color, opacity=0.85, line=dict(color=color, width=2)),
            hovertemplate=(
                f"<b>{row['Country']}</b><br>"
                f"Confirmed: {row['Confirmed']:,}<extra></extra>"
            )
        ))

    fig_bar.update_layout(
        plot_bgcolor='rgba(2,4,25,1)',
        paper_bgcolor='rgba(2,4,25,1)',
        font_color='#ccccff',
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=30, b=40),
        yaxis=dict(gridcolor='rgba(99,102,241,0.2)', color='#818cf8',
                   tickfont=dict(size=11), zerolinecolor='rgba(99,102,241,0.4)'),
        xaxis=dict(color='#a5b4fc', tickfont=dict(size=12)),
        bargap=0.28,
    )
    fig_bar.add_shape(type="rect", xref="paper", yref="paper",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(color="rgba(129,140,248,0.4)", width=1.5),
        fillcolor="rgba(0,0,0,0)")
    fig_bar.update_traces(marker_line_width=0, selector=dict(type="bar"))

    st.markdown("""<div style="border-radius:18px;border:1.5px solid rgba(129,140,248,0.45);
        box-shadow:0 0 25px rgba(129,140,248,0.35),0 0 60px rgba(129,140,248,0.15),
        0 0 100px rgba(192,132,252,0.1);overflow:hidden;padding:4px;background:rgba(2,4,25,1);">
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🥧 Cases Distribution")

    fig_pie = px.pie(
        filtered_df, names='Country', values='Confirmed', hole=0.45,
        color_discrete_sequence=['#818cf8','#f472b6','#34d399','#fbbf24','#c084fc',
                                  '#60a5fa','#fb923c','#a3e635','#e879f9','#2dd4bf'],
        height=440
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(2,4,25,1)', paper_bgcolor='rgba(2,4,25,1)',
        font_color='#ccccff', margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(font=dict(color='#c4c4ff', size=12), bgcolor='rgba(0,0,0,0)'),
    )
    fig_pie.update_traces(
        textfont_color='white', textfont_size=13,
        pull=[0.06] * len(filtered_df),
        marker=dict(line=dict(color='#02041a', width=3)),
        rotation=45,
    )

    st.markdown("""<div style="border-radius:18px;border:1.5px solid rgba(244,114,182,0.45);
        box-shadow:0 0 25px rgba(192,132,252,0.35),0 0 60px rgba(244,114,182,0.2),
        0 0 100px rgba(129,140,248,0.1);overflow:hidden;padding:4px;background:rgba(2,4,25,1);">
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
    # Show full dataset as uniform blue table
    blue_table(filtered_df.reset_index(drop=True))

    # ── Search Fix: search from FULL df, not sidebar-filtered ──
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

    # ── Recovery Rate Ranking ──
    st.subheader("💚 Recovery Rate Ranking")

    ranking = (
        filtered_df[["Country", "Recovery Rate"]]
        .sort_values("Recovery Rate", ascending=False)
        .reset_index(drop=True)
    )
    blue_table(ranking)

    # ── Country Comparison ──
    st.subheader("⚔️ Country Comparison")

    comparison = filtered_df[[
        "Country", "Confirmed", "Deaths", "Recovered", "Recovery Rate"
    ]].sort_values("Confirmed", ascending=False).reset_index(drop=True)

    blue_table(comparison)

    # ── Country Progress Bars ──
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