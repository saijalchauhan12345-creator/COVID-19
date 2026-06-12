import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="COVID Analytics Dashboard",
    page_icon="🦠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>

.main {
    background-color: #f5f7ff;
}

[data-testid="stMetric"] {
    background: white;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)
if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: white;
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
background: linear-gradient(to right,#4F46E5,#EC4899);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
🦠 COVID-19 Analytics Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;'>Interactive Dashboard using Streamlit</p>",
    unsafe_allow_html=True
)

st.divider()

# Sidebar

st.sidebar.header("⚙️ Filters")


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

col1, col2, col3 = st.columns(3)

col1.metric(
    "🦠 Total Cases",
    f"{filtered_df['Confirmed'].sum():,}"
)

col2.metric(
    "💀 Total Deaths",
    f"{filtered_df['Deaths'].sum():,}"
)

col3.metric(
    "💚 Total Recovered",
    f"{filtered_df['Recovered'].sum():,}"
)

# Extra Analytics
if filtered_df["Confirmed"].sum() > 0:

    recovery_rate = (
        filtered_df["Recovered"].sum()
        / filtered_df["Confirmed"].sum()
    ) * 100

    death_rate = (
        filtered_df["Deaths"].sum()
        / filtered_df["Confirmed"].sum()
    ) * 100

    col4, col5 = st.columns(2)

    col4.metric(
        "💚 Recovery Rate",
        f"{recovery_rate:.2f}%"
    )

    col5.metric(
        "💀 Death Rate",
        f"{death_rate:.2f}%"
    )

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["📊 Dashboard", "📋 Dataset", "🏆 Rankings"]
)

# Dashboard Tab
with tab1:

    st.subheader("📊 Confirmed Cases")

    st.bar_chart(
        filtered_df.set_index("Country")["Confirmed"]
    )

    st.subheader("🥧 Cases Distribution")

    fig, ax = plt.subplots()

    ax.pie(
        filtered_df["Confirmed"],
        labels=filtered_df["Country"],
        autopct="%1.1f%%"
    )

    st.pyplot(fig)

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
    f"Average Confirmed Cases Across Selected Countries: {avg_cases:,.0f}"
)

# Ranking Tab
with tab3:

    st.subheader("💚 Recovery Rate Ranking")

    ranking = filtered_df[
        ["Country", "Recovery Rate"]
    ].sort_values(
        "Recovery Rate",
        ascending=False
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

    # 👇 NAYA CODE YAHAN SE ADD KARO

    st.subheader("⚔️ Country Comparison")

    comparison = filtered_df[
        ["Country", "Confirmed", "Deaths", "Recovered"]
    ]

    st.dataframe(
        comparison,
        use_container_width=True
    )

    st.subheader(
        "🏆 Top 3 Countries by Cases"
    )

    top3 = filtered_df.sort_values(
        by="Confirmed",
        ascending=False
    ).head(3)

    st.dataframe(
        top3,
        use_container_width=True
    )

    st.subheader(
        "💚 Recovery Rate Ranking"
    )

    ranking = filtered_df[
        ["Country", "Recovery Rate"]
    ].sort_values(
        "Recovery Rate",
        ascending=False
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

    st.subheader(
        "🏅 Country Progress"
    )

    max_cases = filtered_df[
        "Confirmed"
    ].max()

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