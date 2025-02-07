import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

day_df = pd.read_csv("data/day.csv") 
hour_df = pd.read_csv("data/hour.csv")


st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Title
st.title("🚲 Bike Sharing Data Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Data")

season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
selected_season = st.sidebar.selectbox("Select Season", list(season_map.keys()), format_func=lambda x: season_map[x])

hour_range = st.sidebar.slider("Select Hour Range", 0, 23, (6, 18))

# Apply Filters
filtered_hour_df = hour_df[
    (hour_df["season"] == selected_season) & 
    (hour_df["hr"] >= hour_range[0]) & 
    (hour_df["hr"] <= hour_range[1])
]

st.subheader("📈 Tren Jumlah Penyewa Sepeda")
plt.figure(figsize=(10, 5))
sns.lineplot(data=day_df, x="dteday", y="cnt", marker="o", color="blue")
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Penyewa")
plt.title("Tren Penyewaan Sepeda Harian")
st.pyplot(plt)

# Cuaca Analysis
weather_analysis = filtered_hour_df.groupby("weathersit").agg(
    total_rentals=("cnt", "sum"),
    avg_rentals=("cnt", "mean"),
    median_rentals=("cnt", "median"),
    max_rentals=("cnt", "max"),
    min_rentals=("cnt", "min"),
    count_hours=("cnt", "count")
)

# Jam Analysis
hourly_analysis = filtered_hour_df.groupby("hr").agg(
    total_rentals=("cnt", "sum"),
    avg_rentals=("cnt", "mean"),
    median_rentals=("cnt", "median"),
    max_rentals=("cnt", "max"),
    min_rentals=("cnt", "min"),
    count_hours=("cnt", "count")
)

# Hourly Rental Distribution
st.subheader("📊 Hourly Rental Distribution")
fig, ax = plt.subplots(figsize=(12, 5))
hourly_analysis["total_rentals"].plot(kind="bar", ax=ax, color="skyblue")
ax.set_xlabel("Hour of the Day")
ax.set_ylabel("Total Rentals")
ax.set_title("Total Bike Rentals by Hour (Filtered)")
st.pyplot(fig)

# Rentals by Weather Condition
st.subheader("☁️ Rentals by Weather Condition")
fig, ax = plt.subplots(figsize=(10, 5))
weather_analysis["total_rentals"].plot(kind="bar", ax=ax, color="orange")
ax.set_xlabel("Weather Condition (1=Clear, 2=Mist, 3=Light Rain/Snow, 4=Heavy Rain/Snow)")
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Weather Condition (Filtered)")
st.pyplot(fig)

st.sidebar.markdown("Dhikaa")
