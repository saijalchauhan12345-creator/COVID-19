
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="COVID Analytics Dashboard",
    page_icon="🦠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>

.stApp{
    background: #050816;
    color:white;
}

section[data-testid="stSidebar"]{
    background: linear-gradient(
        180deg,
        #0b0f3d,
        #090b2f
    );
    border-right:1px solid rgba(255,255,255,.1);
}

section[data-testid="stSidebar"] *{
    color:white;
}

[data-testid="stMetric"]{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 25px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,.15);
    box-shadow: 0 0 20px rgba(124,58,237,.35);
}

h1{
    letter-spacing:-2px;
}
            /* Table styling */
.stDataFrame > div, iframe {
    background-color: rgba(15, 15, 40, 0.9) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
thead tr th {
    background-color: rgba(91, 91, 255, 0.2) !important;
    color: #c4c4ff !important;
}
tbody tr td {
    color: #e0e0e0 !important;
    background-color: rgba(15,15,40,0.8) !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
}
tbody tr:hover td {
    background-color: rgba(91,91,255,0.1) !important;
}

</style>
""", unsafe_allow_html=True)
# Load Data
df = pd.read_csv("covid_data.csv")

# Recovery Rate
df["Recovery Rate"] = (
    df["Recovered"] / df["Confirmed"] * 100
)

# Header
st.markdown("""
<h1 style='text-align:center;
font-size:55px;
background:linear-gradient(to right,#4F46E5,#EC4899);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
🦠 COVID Analytics Dashboard
</h1>

<p style='text-align:center;
font-size:18px;
color:#64748B;'>
Interactive Analytics using Streamlit
</p>
""", unsafe_allow_html=True)

st.divider()

# Sidebar
st.sidebar.header("⚙️ Filters")
st.sidebar.markdown("""
# 🌎 FILTERS
Select Countries
""")
selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    df["Country"].unique(),
    default=df["Country"].unique()
)

filtered_df = df[
    df["Country"].isin(selected_countries)
]

# KPI Cards
st.subheader("📌 Key Metrics")
recovery_rate = (
    (filtered_df["Recovered"].sum() / filtered_df["Confirmed"].sum()
) * 100)if filtered_df["Confirmed"].sum() > 0 else 0
death_rate = (
    (filtered_df["Deaths"].sum() / filtered_df["Confirmed"].sum()
) * 100)if filtered_df["Confirmed"].sum() > 0 else 0
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "🦠 Cases",
    f"{filtered_df['Confirmed'].sum():,}"
)

col2.metric(
    "💀 Deaths",
    f"{filtered_df['Deaths'].sum():,}"
)

col3.metric(
    "💚 Recovered",
    f"{filtered_df['Recovered'].sum():,}"
)

col4.metric(
    "📈 Recovery %",
    f"{recovery_rate:.2f}%"
)

col5.metric(
    "📉 Death %",
    f"{death_rate:.2f}%"
)
# Tabs
tab1, tab2, tab3 = st.tabs(
    ["📊 Dashboard", "📋 Dataset", "🏆 Rankings"]
)

# Dashboard Tab
with tab1:

    st.subheader("📊 Confirmed Cases")
fig_bar = px.bar(
    filtered_df,
    x='Country',
    y='Confirmed',
    color='Country',
    color_discrete_sequence=['#818cf8','#c084fc','#f472b6','#fbbf24','#34d399'],
    height=320
)
fig_bar.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(15,15,40,0.9)',
    font_color='#ccccff',
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=40),
   yaxis=dict(gridcolor='rgba(255,255,255,0.07)'),
    xaxis=dict(color='#888'),
)
st.plotly_chart(fig_bar, use_container_width=True)


st.subheader("🥧 Cases Distribution")

fig, ax = plt.subplots(
    figsize=(7,7)
)

colors = [
    "#8B5CF6",
    "#EC4899",
    "#06B6D4",
    "#10B981",
    "#F59E0B"
    ]

fig_pie = px.pie(
            filtered_df,
            names='Country',
            values='Confirmed',
            hole=0.4,
            color_discrete_sequence=['#818cf8','#f87171','#34d399','#fbbf24','#c084fc'],
            height=320
        )
fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(15,15,40,0.9)',
            font_color='#ccccff',
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(color='#aaa', size=11)),
        )
fig_pie.update_traces(
            textfont_color='white',
            marker=dict(line=dict(color='#07071a', width=2))
        )
st.plotly_chart(fig_pie, use_container_width=True)

highest = filtered_df.loc[
        filtered_df["Confirmed"].idxmax(),
        "Country"
    ]

lowest = filtered_df.loc[
        filtered_df["Confirmed"].idxmin(),
        "Country"
    ]

st.info(
        f"🏆 Highest Cases: {highest} | 🌱 Lowest Cases: {lowest}"
    )

# Dataset Tab
with tab2:

    st.download_button(
        label="📥 Download Dataset",
        data=filtered_df.to_csv(index=False),
        file_name="covid_data.csv",
        mime="text/csv"
    )

    st.subheader("📋 Dataset")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    search = st.text_input(
        "🔍 Search Country"
    )

    if search:

        result = filtered_df[
            filtered_df["Country"]
            .str.contains(
                search,
                case=False
            )
        ]

        st.dataframe(result)

    st.subheader("📈 Trend Analysis")

    avg_cases = filtered_df["Confirmed"].mean()

    st.info(
        f"📈 Average Confirmed Cases: {avg_cases:,.0f}"
    )

# Ranking Tab
with tab3:

    st.success("🥇 Top Performing Countries")

    top3 = filtered_df.sort_values(
        by="Confirmed",
        ascending=False
    ).head(3)

    for i,row in top3.iterrows():

     st.success(
        f"🏆 {row['Country']} — {row['Confirmed']:,} cases"
    )
    st.subheader("💚 Recovery Rate Ranking")

    ranking = filtered_df[
        ["Country", "Recovery Rate"]
    ].sort_values(
        "Recovery Rate",
        ascending=False
    )

st.dataframe(
    ranking.style.set_properties(**{
        'background-color': 'rgba(15,15,40,0.9)',
        'color': '#e0e0e0',
        'border-color': 'rgba(255,255,255,0.1)'
    }).highlight_max(color='rgba(91,91,255,0.3)'),
    use_container_width=True
)
st.subheader("⚔️ Country Comparison")

st.dataframe(
    comparison.style.set_properties(**{
        'background-color': 'rgba(15,15,40,0.9)',
        'color': '#e0e0e0',
        'border-color': 'rgba(255,255,255,0.1)'
    }),
    use_container_width=True
)

st.dataframe(
        comparison,
        use_container_width=True
    )

st.subheader("🏅 Country Progress")

max_cases = filtered_df["Confirmed"].max()

for _, row in filtered_df.iterrows():

        st.write(
            f"🌍 {row['Country']} - {row['Confirmed']:,}"
        )

        st.progress(
            int(
                (row["Confirmed"] / max_cases)
                * 100
            )
        )

# Footer
st.markdown("---")

st.markdown(
    "<center>Made with ❤️ by Saijal Chauhan</center>",
    unsafe_allow_html=True
)
