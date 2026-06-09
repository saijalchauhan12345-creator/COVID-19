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

# Custom Styling
st.markdown("""
<style>

.main {
    background-color: #f5f7ff;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    border-left: 6px solid #4F46E5;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}

h1 {
    text-align: center;
    color: #4F46E5;
}

</style>
""", unsafe_allow_html=True)

# Load Data
df = pd.read_csv("covid_data.csv")

# Title
st.markdown(
    "<h1>🦠 COVID-19 Analytics Dashboard</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Interactive COVID Dashboard using Streamlit & Plotly</p>",
    unsafe_allow_html=True
)

st.divider()

# Sidebar
st.sidebar.header("⚙️ Filters")

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    df["Country"].unique(),
    default=df["Country"].unique()[:3]
)

if selected_countries:
    filtered_df = df[df["Country"].isin(selected_countries)]
else:
    filtered_df = df

# KPI Cards
st.subheader("📌 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

total_cases = df['Confirmed'].sum()
total_deaths = df['Deaths'].sum()
total_recovered = df['Recovered'].sum()

recovery_rate = (total_recovered / total_cases * 100) if total_cases > 0 else 0
death_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0

col1.metric(
    "🦠 Total Cases",
    f"{total_cases:,}"
)

col2.metric(
    "💀 Total Deaths",
    f"{total_deaths:,}"
)

col3.metric(
    "💚 Total Recovered",
    f"{total_recovered:,}"
)

col4.metric(
    "📊 Recovery Rate",
    f"{recovery_rate:.2f}%"
)

col5.metric(
    "⚠️ Death Rate",
    f"{death_rate:.2f}%"
)

st.divider()

# Selected Country Data
countries_text = ", ".join(selected_countries) if selected_countries else "No countries selected"
st.subheader(f"🌍 {countries_text} Overview")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# Confirmed Cases Chart
st.subheader("📊 Confirmed Cases by Country")

fig1 = px.bar(
    df,
    x="Country",
    y="Confirmed",
    color="Country",
    title="Confirmed Cases by Country"
)

st.plotly_chart(fig1, use_container_width=True)

# Recovery vs Deaths
st.subheader("📈 Recovered vs Deaths Comparison")

fig2 = px.bar(
    df,
    x="Country",
    y=["Recovered", "Deaths"],
    barmode="group",
    title="Recovered vs Deaths"
)

st.plotly_chart(fig2, use_container_width=True)

# Pie Chart
st.subheader("🥧 Cases Distribution")

col_pie1, col_pie2 = st.columns([1, 1])

with col_pie1:
    fig, ax = plt.subplots(figsize=(6, 5))
    
    ax.pie(
        df["Confirmed"],
        labels=df["Country"],
        autopct="%1.1f%%"
    )
    
    st.pyplot(fig)

st.divider()

# Search Feature
st.subheader("🔍 Search Country")

search = st.text_input("Enter Country Name")

if search:
    result = df[df["Country"].str.contains(search, case=False)]
    st.dataframe(result, use_container_width=True)

st.divider()

# Download Button
st.download_button(
    label="📥 Download Dataset",
    data=df.to_csv(index=False),
    file_name="covid_data.csv",
    mime="text/csv"
)

st.divider()

# Full Dataset
st.subheader("📋 Complete Dataset")
st.dataframe(df, use_container_width=True)

# Highest Cases Country
top_country = df.loc[df["Confirmed"].idxmax(), "Country"]

st.success(
    f"🏆 Country with Highest Cases: {top_country}"
)

# Footer
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ by Saijal Chauhan</center>",
    unsafe_allow_html=True
)