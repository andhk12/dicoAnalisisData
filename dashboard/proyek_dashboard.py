# proyek_dashboard.py (versi cocok dengan data yang sudah dicleaning)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# RAW URL (bukan refs/heads)
DAY_URL  = "https://raw.githubusercontent.com/andhk12/dicoAnalisisData/main/data/new_day_df.csv"
HOUR_URL = "https://raw.githubusercontent.com/andhk12/dicoAnalisisData/main/data/new_hour_df.csv"

# Load Data 
@st.cache_data
def load_data(day_url: str, hour_url: str):
    day_df  = pd.read_csv(day_url)
    hour_df = pd.read_csv(hour_url)

    # pastikan tanggal & year
    day_df["dteday"]  = pd.to_datetime(day_df["dteday"], errors="coerce")
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"], errors="coerce")
    day_df["year"]    = day_df["dteday"].dt.year
    hour_df["year"]   = hour_df["dteday"].dt.year

    # pastikan numerik untuk kolom penting
    for col in ["cnt", "casual", "registered"]:
        if col in day_df.columns:
            day_df[col] = pd.to_numeric(day_df[col], errors="coerce")
    for col in ["cnt", "hr"]:
        if col in hour_df.columns:
            hour_df[col] = pd.to_numeric(hour_df[col], errors="coerce")

    # normalisasi label (trim spasi, jika ada)
    for df in (day_df, hour_df):
        for cat_col in ["season", "weekday", "weathersit", "workingday"]:
            if cat_col in df.columns and df[cat_col].dtype == "object":
                df[cat_col] = df[cat_col].astype(str).str.strip()

    return day_df, hour_df

day_df, hour_df = load_data(DAY_URL, HOUR_URL)

if day_df.empty or hour_df.empty:
    st.error("Gagal memuat data. Periksa kembali URL raw GitHub dan struktur file CSV.")
    st.stop()

# Sidebar Filters (pakai kolom hasil cleaning) 
st.sidebar.title("Filter Data")

# Nilai unik dari data hasil cleaning 
all_seasons  = sorted(day_df["season"].dropna().unique().tolist())            if "season" in day_df.columns else []
all_weathers = sorted(day_df["weathersit"].dropna().unique().tolist())        if "weathersit" in day_df.columns else []
all_weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
all_weekdays = [d for d in all_weekdays if ("weekday" in day_df.columns and d in day_df["weekday"].unique())]

selected_seasons  = st.sidebar.multiselect("Pilih Musim", options=all_seasons,  default=all_seasons)
selected_weathers = st.sidebar.multiselect("Pilih Cuaca", options=all_weathers, default=all_weathers)
selected_weekdays = st.sidebar.multiselect("Pilih Hari",  options=all_weekdays, default=all_weekdays)

selected_hours = st.sidebar.slider("Rentang Jam (hour_df)", 0, 23, (0, 23))
only_workingday = st.sidebar.checkbox("Hanya Hari Kerja (workingday='Workingday')", value=False)
agg_choice = st.sidebar.radio("Agregasi untuk grafik", options=["Rata-rata", "Total"], index=0)
agg_fn = {"Rata-rata": "mean", "Total": "sum"}[agg_choice]

# Terapkan filter ke salinan
df_day  = day_df.copy()
df_hour = hour_df.copy()

# Filter by season
if selected_seasons and "season" in df_day.columns:
    df_day  = df_day[df_day["season"].isin(selected_seasons)]
    if "season" in df_hour.columns:
        df_hour = df_hour[df_hour["season"].isin(selected_seasons)]

# Filter by weather
if selected_weathers and "weathersit" in df_day.columns:
    df_day  = df_day[df_day["weathersit"].isin(selected_weathers)]
    if "weathersit" in df_hour.columns:
        df_hour = df_hour[df_hour["weathersit"].isin(selected_weathers)]

# Filter by weekday
if selected_weekdays and "weekday" in df_day.columns:
    df_day  = df_day[df_day["weekday"].isin(selected_weekdays)]
    if "weekday" in df_hour.columns:
        df_hour = df_hour[df_hour["weekday"].isin(selected_weekdays)]

# Filter workingday (perhatikan: sekarang berupa string 'Workingday'/'Holiday')
if only_workingday:
    if "workingday" in df_day.columns:
        df_day = df_day[df_day["workingday"] == "Workingday"]
    if "workingday" in df_hour.columns:
        df_hour = df_hour[df_hour["workingday"] == "Workingday"]

# Filter jam
h0, h1 = selected_hours
if "hr" in df_hour.columns:
    df_hour = df_hour[(df_hour["hr"] >= h0) & (df_hour["hr"] <= h1)]

# Header 
st.title("Bike Sharing Dashboard")
st.markdown(
    f"""
**Filter aktif:** Musim = `{', '.join(selected_seasons) or 'All'}`, 
Cuaca = `{', '.join(selected_weathers) or 'All'}`, 
Hari = `{', '.join(selected_weekdays) or 'All'}`, 
Jam = `{selected_hours[0]}–{selected_hours[1]}`, 
Workingday = `{"Ya" if only_workingday else "Tidak"}`, 
Agregasi = `{agg_choice}`.
"""
)

# 1) Tren per Musim & Tahun 
st.subheader("Tren Penyewaan Sepeda per Musim & Tahun")
if df_day.empty:
    st.info("Data day_df kosong setelah filter. Silakan longgarkan filter.")
else:
    trend = (
        df_day.groupby(["year", "season"], as_index=False)["cnt"]
        .agg(agg_fn)
        .rename(columns={"cnt": "value"})
        .sort_values(["season", "year"])
    )
    if trend.empty:
        st.info("Tren kosong untuk kombinasi filter saat ini.")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=trend, x="year", y="value", hue="season", marker="o", ax=ax)
        ax.set_xlabel("Tahun")
        ax.set_ylabel(f"{agg_choice} Penyewa")
        ax.set_title(f"Tren Penyewaan Sepeda per Musim & Tahun ({agg_choice})")
        ax.grid(alpha=0.3)
        st.pyplot(fig, clear_figure=True)

# 2) Distribusi per Jam 
st.subheader("Distribusi Penyewaan Sepeda per Jam")
if df_hour.empty or ("hr" not in df_hour.columns):
    st.info("Data hour_df kosong atau kolom 'hr' tidak ada. Bagian ini dilewati.")
else:
    df_plot = df_hour.dropna(subset=["hr", "cnt"]).copy()
    df_plot["hr"]  = pd.to_numeric(df_plot["hr"], errors="coerce")
    df_plot["cnt"] = pd.to_numeric(df_plot["cnt"], errors="coerce")
    df_plot = df_plot.dropna(subset=["hr", "cnt"])
    if df_plot.empty:
        st.info("Tidak ada data valid untuk plotting distribusi per jam.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.boxplot(data=df_plot, x="hr", y="cnt", ax=ax)
            ax.set_xlabel("Jam")
            ax.set_ylabel("Jumlah Penyewa (cnt)")
            ax.set_title("Distribusi (Boxplot) Penyewaan per Jam")
            ax.grid(axis="y", alpha=0.3)
            st.pyplot(fig, clear_figure=True)
        with col2:
            agg_per_hour = (
                df_plot.groupby("hr", as_index=False)["cnt"]
                .agg(agg_fn)
                .rename(columns={"cnt": "value"})
                .sort_values("hr")
            )
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(agg_per_hour["hr"], agg_per_hour["value"])
            ax.set_xlabel("Jam")
            ax.set_ylabel(f"{agg_choice} Penyewa")
            ax.set_title(f"{agg_choice} Penyewaan per Jam")
            ax.grid(axis="y", alpha=0.3)
            st.pyplot(fig, clear_figure=True)

# 3) Penyewaan berdasarkan Cuaca 
st.subheader("Penyewaan Sepeda Berdasarkan Cuaca")
if df_day.empty or ("weathersit" not in df_day.columns):
    st.info("Data day_df kosong atau kolom 'weathersit' tidak ada.")
else:
    weather_agg = (
        df_day.groupby("weathersit", as_index=False)["cnt"]
        .agg(agg_fn)
        .rename(columns={"cnt": "value"})
        .sort_values("value", ascending=False)
    )
    if weather_agg.empty:
        st.info("Tidak ada data cuaca untuk kombinasi filter saat ini.")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=weather_agg, x="weathersit", y="value", ax=ax)
        ax.set_xlabel("Kondisi Cuaca")
        ax.set_ylabel(f"{agg_choice} Penyewa")
        ax.set_title("Penyewaan Berdasarkan Cuaca")
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig, clear_figure=True)

# 4) Casual vs Registered
st.subheader("Casual vs Registered per Tahun")
if df_day.empty or not set(["casual", "registered"]).issubset(df_day.columns):
    st.info("Kolom 'casual'/'registered' tidak ditemukan pada day_df.")
else:
    user_trend = (
        df_day.groupby("year", as_index=False)[["casual", "registered"]]
        .agg(agg_fn)
        .melt(id_vars="year", var_name="user_type", value_name="value")
        .sort_values(["user_type", "year"])
    )
    if user_trend.empty:
        st.info("Tidak ada data untuk perbandingan casual vs registered.")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=user_trend, x="year", y="value", hue="user_type", ax=ax)
        ax.set_xlabel("Tahun")
        ax.set_ylabel(f"{agg_choice} Penyewa")
        ax.set_title(f"Casual vs Registered per Tahun ({agg_choice})")
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig, clear_figure=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Made by Dhikaa")

# =============== 5) HEATMAP: Hari × Jam ===============
st.subheader("🔥 Heatmap Penyewaan — Hari × Jam")

if df_hour.empty or ("hr" not in df_hour.columns) or ("weekday" not in df_hour.columns):
    st.info("Data hour_df kosong atau kolom 'hr' / 'weekday' tidak ada. Heatmap Hari × Jam dilewati.")
else:
    df_hj = df_hour.dropna(subset=["hr", "cnt", "weekday"]).copy()
    df_hj["hr"]  = pd.to_numeric(df_hj["hr"], errors="coerce")
    df_hj["cnt"] = pd.to_numeric(df_hj["cnt"], errors="coerce")
    df_hj = df_hj.dropna(subset=["hr", "cnt"])

    if df_hj.empty:
        st.info("Tidak ada data valid untuk Heatmap Hari × Jam.")
    else:
        # urutan hari (sesuai label yang kamu pakai setelah cleaning)
        order_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        # bikin pivot
        pivot_hj = (
            df_hj.pivot_table(index="weekday", columns="hr", values="cnt", aggfunc=agg_fn)
                 .reindex(index=[d for d in order_days if d in df_hj["weekday"].unique()])
                 .sort_index(axis=1)  # kolom jam 0..23
        )

        # info ringkas
        with st.expander("🔎 Ringkasan Heatmap Hari × Jam"):
            st.write("Shape:", pivot_hj.shape)
            st.dataframe(pivot_hj.head())

        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(pivot_hj, cmap="YlGnBu", annot=False, cbar_kws={"label": f"{agg_choice} Penyewa"})
        ax.set_xlabel("Jam")
        ax.set_ylabel("Hari")
        ax.set_title(f"Heatmap Penyewaan (Hari × Jam) — ({agg_choice})")
        st.pyplot(fig, clear_figure=True)

# =============== 6) HEATMAP: Musim × Jam ===============
st.subheader("🔥 Heatmap Penyewaan — Musim × Jam")

if df_hour.empty or ("hr" not in df_hour.columns) or ("season" not in df_hour.columns):
    st.info("Data hour_df kosong atau kolom 'hr' / 'season' tidak ada. Heatmap Musim × Jam dilewati.")
else:
    df_sj = df_hour.dropna(subset=["hr", "cnt", "season"]).copy()
    df_sj["hr"]  = pd.to_numeric(df_sj["hr"], errors="coerce")
    df_sj["cnt"] = pd.to_numeric(df_sj["cnt"], errors="coerce")
    df_sj = df_sj.dropna(subset=["hr", "cnt"])

    if df_sj.empty:
        st.info("Tidak ada data valid untuk Heatmap Musim × Jam.")
    else:
        # urutan musim sesuai label hasil cleaning
        order_seasons = ["Spring", "Summer", "Fall", "Winter"]
        pivot_sj = (
            df_sj.pivot_table(index="season", columns="hr", values="cnt", aggfunc=agg_fn)
                .reindex(index=[s for s in order_seasons if s in df_sj["season"].unique()])
                .sort_index(axis=1)
        )

        with st.expander("🔎 Ringkasan Heatmap Musim × Jam"):
            st.write("Shape:", pivot_sj.shape)
            st.dataframe(pivot_sj.head())

        fig, ax = plt.subplots(figsize=(10, 3.6))
        sns.heatmap(pivot_sj, cmap="YlGnBu", annot=False, cbar_kws={"label": f"{agg_choice} Penyewa"})
        ax.set_xlabel("Jam")
        ax.set_ylabel("Musim")
        ax.set_title(f"Heatmap Penyewaan (Musim × Jam) — ({agg_choice})")
        st.pyplot(fig, clear_figure=True)
