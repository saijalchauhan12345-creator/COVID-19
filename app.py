import plotly.express as px
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="COVID Analytics Dashboard",
    page_icon="🦠",
    layout="wide"
)

# Load Data
df = pd.read_csv("covid_data.csv")

# Title
st.title("🦠 COVID-19 Analytics Dashboard")
st.markdown("A simple responsive dashboard built using Streamlit")

# Metrics
col1, col2, col3 = st.columns(3)

col1.metric("Total Cases", f"{df['Confirmed'].sum():,}")
col2.metric("Total Deaths", f"{df['Deaths'].sum():,}")
col3.metric("Total Recovered", f"{df['Recovered'].sum():,}")

st.divider()

# Sidebar
st.sidebar.header("Filters")

country = st.sidebar.selectbox(
    "Select Country",
    df["Country"]
)

filtered_df = df[df["Country"] == country]

# Country Data
st.subheader(f"📍 {country} Statistics")
st.dataframe(filtered_df)

st.divider()

# Bar Chart
st.subheader("📊 Confirmed Cases by Country")
fig = px.bar(
    df,
    x="Country",
    y="Confirmed",
    title="Confirmed Cases by Country"
)

st.plotly_chart(fig, use_container_width=True)

# Pie Chart
st.subheader("📈 Recovered vs Deaths")

fig2 = px.bar(
    df,
    x="Country",
    y=["Recovered", "Deaths"],
    barmode="group",
    title="Recovered vs Deaths Comparison"
)

st.plotly_chart(fig2, use_container_width=True)
# Search
st.subheader("🔍 Search Country")

search = st.text_input("Enter Country Name")

if search:
    result = df[df["Country"].str.contains(search, case=False)]
    st.dataframe(result)

st.divider()
st.download_button(
    label="📥 Download Dataset",
    data=df.to_csv(index=False),
    file_name="covid_data.csv",
    mime="text/csv"
)

# Dataset
st.subheader("📋 Full Dataset")
st.dataframe(df)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")