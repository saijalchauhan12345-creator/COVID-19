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

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Overview",
    "🌍 Country Analysis",
    "📊 Charts",
    "🔍 Search & Download"
])

# ============== TAB 1: OVERVIEW ==============
with tab1:
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
    
    # Highest Cases Country
    top_country = df.loc[df["Confirmed"].idxmax(), "Country"]
    top_country_data = df[df["Country"] == top_country].iloc[0]
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.success(f"🏆 Highest Cases: {top_country}")
        st.metric("Cases", f"{top_country_data['Confirmed']:,}")
    
    with col_info2:
        highest_deaths_country = df.loc[df["Deaths"].idxmax(), "Country"]
        st.info(f"⚠️ Most Deaths: {highest_deaths_country}")
        st.metric("Deaths", f"{df[df['Country'] == highest_deaths_country].iloc[0]['Deaths']:,}")
    
    with col_info3:
        highest_recovery_country = df.loc[df["Recovered"].idxmax(), "Country"]
        st.success(f"💚 Most Recovered: {highest_recovery_country}")
        st.metric("Recovered", f"{df[df['Country'] == highest_recovery_country].iloc[0]['Recovered']:,}")

# ============== TAB 2: COUNTRY ANALYSIS ==============
with tab2:
    st.subheader("🌍 Filtered Country Overview")
    
    countries_text = ", ".join(selected_countries) if selected_countries else "No countries selected"
    st.write(f"**Selected Countries:** {countries_text}")
    
    st.subheader("📋 Country Data")
    st.dataframe(filtered_df, use_container_width=True)
    
    st.divider()
    
    # Detailed Statistics
    st.subheader("📈 Selected Countries Statistics")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    filtered_cases = filtered_df['Confirmed'].sum()
    filtered_deaths = filtered_df['Deaths'].sum()
    filtered_recovered = filtered_df['Recovered'].sum()
    
    with col_stat1:
        st.metric("Total Cases", f"{filtered_cases:,}")
    with col_stat2:
        st.metric("Total Deaths", f"{filtered_deaths:,}")
    with col_stat3:
        st.metric("Total Recovered", f"{filtered_recovered:,}")

# ============== TAB 3: CHARTS ==============
with tab3:
    st.subheader("📊 Visual Analytics")
    
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
    
    st.divider()
    
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
    
    st.divider()
    
    # Pie Chart
    col_pie1, col_pie2 = st.columns([1, 1])
    
    with col_pie1:
        st.subheader("🥧 Cases Distribution")
        fig_pie1, ax_pie1 = plt.subplots(figsize=(8, 6))
        
        ax_pie1.pie(
            df["Confirmed"],
            labels=df["Country"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax_pie1.set_title("Confirmed Cases Distribution")
        
        st.pyplot(fig_pie1)
    
    with col_pie2:
        st.subheader("🥧 Deaths Distribution")
        fig_pie2, ax_pie2 = plt.subplots(figsize=(8, 6))
        
        ax_pie2.pie(
            df["Deaths"],
            labels=df["Country"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax_pie2.set_title("Deaths Distribution")
        
        st.pyplot(fig_pie2)

# ============== TAB 4: SEARCH & DOWNLOAD ==============
with tab4:
    st.subheader("🔍 Search Country Data")
    
    search = st.text_input("Enter Country Name to Search")
    
    if search:
        result = df[df["Country"].str.contains(search, case=False)]
        
        if not result.empty:
            st.success(f"✅ Found {len(result)} match(es)")
            st.dataframe(result, use_container_width=True)
        else:
            st.warning(f"⚠️ No countries found matching '{search}'")
    else:
        st.info("📝 Enter a country name to search")
    
    st.divider()
    
    st.subheader("📥 Download Options")
    
    col_down1, col_down2 = st.columns(2)
    
    with col_down1:
        # Download full dataset
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=df.to_csv(index=False),
            file_name="covid_data_full.csv",
            mime="text/csv"
        )
    
    with col_down2:
        # Download filtered dataset
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=filtered_df.to_csv(index=False),
            file_name="covid_data_filtered.csv",
            mime="text/csv"
        )
    
    st.divider()
    
    st.subheader("📋 Complete Dataset")
    st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ by Saijal Chauhan</center>",
    unsafe_allow_html=True
)  