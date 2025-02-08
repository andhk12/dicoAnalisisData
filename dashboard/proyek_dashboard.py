import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

day_df = pd.read_csv("D:\Study\Dicoding\latihan1\Bike-sharing-dataset\day.csv") 
hour_df = pd.read_csv("D:\Study\Dicoding\latihan1\Bike-sharing-dataset\hour.csv")

season_dict = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_dict = {1: "Cerah", 2: "Berawan", 3: "Hujan", 4: "Salju"}

day_df["season_name"] = day_df["season"].map(season_dict)
hour_df["season_name"] = hour_df["season"].map(season_dict)

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

day_df["year"] = day_df["dteday"].dt.year
hour_df["year"] = hour_df["dteday"].dt.year

# Sidebar untuk filter
st.sidebar.title("🎛️ Filter Data")
selected_season = st.sidebar.selectbox("📅 Pilih Musim", day_df["season_name"].unique())
hour_range = st.sidebar.slider("⏳ Pilih Rentang Jam", 0, 23, (0, 23))

# Filter dataset berdasarkan pilihan
filtered_hour_df = hour_df[
    (hour_df["season_name"] == selected_season) & 
    (hour_df["hr"] >= hour_range[0]) & 
    (hour_df["hr"] <= hour_range[1])
]

# Hitung jumlah tren per musim dan tahun
trend_per_season = filtered_hour_df.groupby(["year", "season_name"])["cnt"].sum().reset_index()

# **1. Tren Penyewaan Sepeda Per Musim**
st.title("🚲 Analisis Tren Penyewaan Sepeda")
st.subheader(f"Musim: {selected_season} | Rentang Jam: {hour_range[0]} - {hour_range[1]}")

fig, ax = plt.subplots()
for year in trend_per_season["year"].unique():
    yearly_data = trend_per_season[trend_per_season["year"] == year]
    ax.bar(str(year), yearly_data["cnt"].values[0], label=f"{selected_season} {year}")

ax.set_ylabel("Jumlah Penyewa")
ax.set_title("Tren Penyewaan Sepeda Per Musim")
ax.legend()
st.pyplot(fig)

# **2. Distribusi Penyewaan Sepeda Per Jam**
st.subheader("⏳ Distribusi Penyewaan Sepeda Per Jam")

fig, ax = plt.subplots()
filtered_hour_df.groupby("hr")["cnt"].sum().plot(kind="bar", ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Jumlah Penyewa")
ax.set_title(f"Distribusi Penyewaan Sepeda pada Season {selected_season}")

st.pyplot(fig)

# **3. Penyewaan Sepeda Berdasarkan Cuaca**
st.subheader("🌦️ Penyewaan Sepeda Berdasarkan Cuaca")

filtered_hour_df["weathersit"] = filtered_hour_df["weathersit"].map(weather_dict)
weather_trend = filtered_hour_df.groupby("weathersit")["cnt"].sum()

fig, ax = plt.subplots()
weather_trend.plot(kind="bar", ax=ax)
ax.set_ylabel("Jumlah Penyewa")
ax.set_xlabel("Kondisi Cuaca")
ax.set_title(f"Penyewaan Sepeda berdasarkan Cuaca (Season {selected_season})")
st.pyplot(fig)

st.sidebar.markdown("Dhikaa")
