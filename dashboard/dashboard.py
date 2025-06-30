import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px 

# Mengatur style seaborn
sns.set(style='dark')

# Fungsi dan Persiapan Data
def load_data():
    """Memuat dan membersihkan data dari file CSV."""
    df = pd.read_csv("main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Membuat kolom label yang mudah dibaca untuk filter 
    df['season_label'] = df['season'].map({
        'Spring': '1: Musim Semi', 
        'Summer': '2: Musim Panas', 
        'Fall': '3: Musim Gugur', 
        'Winter': '4: Musim Dingin'
    })
    
    df['weathersit_label'] = df['weathersit'].map({
        'Clear/Few clouds/Partly cloudy': '1: Cerah/Berawan',
        'Mist + Cloudy/Mist + Broken clouds/Mist + Few clouds/Mist': '2: Berkabut/Mendung',
        'Light Snow/Light Rain + Thunderstorm + Scattered clouds': '3: Hujan/Salju Ringan',
        'Heavy Rain + Ice Pallets + Thunderstorm + Mist/Snow + Fog': '4: Cuaca Buruk'
    })
    return df

def categorize_hour(hr):
    """Mengelompokkan jam ke dalam kategori waktu (Pagi, Siang, Sore, Malam)."""
    if 1 <= hr < 12: 
        return "Pagi"
    elif 12 <= hr < 16:
        return "Siang"
    elif 16 <= hr <= 18:
        return "Sore"
    else:
        return "Malam" 

# Memuat data
data = load_data()
data['time_of_day'] = data['hr'].apply(categorize_hour)

# Sidebar untuk Filter Interaktif 
st.sidebar.image("sepeda.jpg", use_column_width=True) 
st.sidebar.title("🚲 Filter Data")

# Filter Tanggal
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    min_value=data['dteday'].min().date(),
    max_value=data['dteday'].max().date(),
    value=[data['dteday'].min().date(), data['dteday'].max().date()]
)

# Filter Musim dan Cuaca
season_filter = st.sidebar.multiselect(
    "Pilih Musim",
    options=data['season_label'].sort_values().unique(),
    default=data['season_label'].unique()
)

weather_filter = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
    options=data['weathersit_label'].sort_values().unique(),
    default=data['weathersit_label'].unique()
)

# Filter Tipe Pengguna untuk ditampilkan di grafik
user_type_map = {
    'Total Penyewa': 'cnt',
    'Penyewa Kasual': 'casual',
    'Penyewa Terdaftar': 'registered'
}
selected_user_type_label = st.sidebar.radio(
    "Tampilkan Data Untuk:",
    user_type_map.keys()
)
selected_metric = user_type_map[selected_user_type_label]

# Menerapkan semua filter ke data
data_filtered = data[
    (data['dteday'].dt.date >= start_date) & 
    (data['dteday'].dt.date <= end_date) &
    (data['season_label'].isin(season_filter)) &
    (data['weathersit_label'].isin(weather_filter))
]

# Layout Utama Dashboard
st.title("Dashboard Analisis Penyewaan Sepeda 🚴")
st.markdown("Dasbor ini menyajikan analisis interaktif terhadap data penyewaan sepeda.")

# Ringkasan Data Utama
st.subheader("Ringkasan Data")
col1, col2, col3 = st.columns(3)
col1.metric("Penyewa Kasual", f"{data_filtered['casual'].sum():,}")
col2.metric("Penyewa Terdaftar", f"{data_filtered['registered'].sum():,}")
col3.metric("Total Penyewaan", f"{data_filtered['cnt'].sum():,}")

# --- Jawaban Pertanyaan Bisnis dengan Visualisasi Interaktif (Plotly) ---

# Pertanyaan 1: Pengaruh Musim dan Cuaca (REVISI: Bar chart dengan Plotly)
st.subheader(f"Rata-Rata {selected_user_type_label} Berdasarkan Musim & Cuaca")

col1, col2 = st.columns(2)

with col1:
    season_data = data_filtered.groupby('season_label')[selected_metric].mean().reset_index()
    fig_season = px.bar(
        season_data,
        x='season_label',
        y=selected_metric,
        title="Berdasarkan Musim",
        labels={'season_label': 'Musim', selected_metric: f'Rata-Rata {selected_user_type_label}'},
        color_discrete_sequence=['#4c78a8'] 
    )
    st.plotly_chart(fig_season, use_container_width=True)

with col2:
    weather_data = data_filtered.groupby('weathersit_label')[selected_metric].mean().reset_index()
    fig_weather = px.bar(
        weather_data,
        x='weathersit_label',
        y=selected_metric,
        title="Berdasarkan Kondisi Cuaca",
        labels={'weathersit_label': 'Kondisi Cuaca', selected_metric: f'Rata-Rata {selected_user_type_label}'},
        color_discrete_sequence=['#54a24b'] 
    )
    st.plotly_chart(fig_weather, use_container_width=True)

# Pertanyaan 2: Pola pada Hari Kerja, Akhir Pekan, dan Hari Libur 
st.subheader(f"Total {selected_user_type_label}: Hari Kerja vs. Hari Libur")

col1, col2 = st.columns(2)

with col1:
    workingday_data = data_filtered.groupby('workingday')[selected_metric].sum().reset_index()
    
    fig_workday = px.bar(
        workingday_data,
        x='workingday', 
        y=selected_metric,
        title="Berdasarkan Hari Kerja",
        labels={'workingday': 'Tipe Hari', selected_metric: f'Total {selected_user_type_label}'},
        color_discrete_sequence=['#e45756'],
        category_orders={"workingday": ["Working Day", "Non-Working Day"]}
    )
    st.plotly_chart(fig_workday, use_container_width=True)

with col2:
    holiday_data = data_filtered.groupby('holiday')[selected_metric].sum().reset_index()

    
    fig_holiday = px.bar(
        holiday_data,
        x='holiday',  
        y=selected_metric,
        title="Berdasarkan Hari Libur Nasional",
        labels={'holiday': 'Tipe Hari', selected_metric: f'Total {selected_user_type_label}'},
        color_discrete_sequence=['#f28e2b'],
        # Mengatur urutan bar
        category_orders={"holiday": ["Non-Holiday", "Holiday"]}
    )
    st.plotly_chart(fig_holiday, use_container_width=True)

# Pertanyaan 3: Tren Waktu dalam Sehari 
st.subheader(f"Tren {selected_user_type_label} Berdasarkan Waktu")

# 1. Rata-rata per Kategori Waktu
time_of_day_data = data_filtered.groupby("time_of_day")[selected_metric].mean().reindex(["Pagi", "Siang", "Sore", "Malam"]).reset_index()
fig_time_of_day = px.bar(
    time_of_day_data,
    x='time_of_day',
    y=selected_metric,
    title="Rata-Rata Penyewaan per Kategori Waktu",
    labels={'time_of_day': 'Waktu dalam Sehari', selected_metric: 'Rata-Rata Jumlah Sewa'},
    color_discrete_sequence=['#76b7b2']
)
st.plotly_chart(fig_time_of_day, use_container_width=True)

# 2. Tren Harian Interaktif
st.markdown("### Tren Distribusi Penyewa per Jam Berdasarkan Hari")
hourly_trend_data = data_filtered.groupby(['hr', 'weekday'])[selected_metric].mean().reset_index()
fig_hourly = px.line(
    hourly_trend_data,
    x='hr',
    y=selected_metric,
    color='weekday',
    title="Tren Interaktif per Jam",
    labels={'hr': 'Jam', selected_metric: 'Rata-Rata Jumlah Sewa', 'weekday': 'Hari'},
    markers=True
)
st.plotly_chart(fig_hourly, use_container_width=True)


st.caption("© 2025 Sepedashboard. All rights reserved.")
