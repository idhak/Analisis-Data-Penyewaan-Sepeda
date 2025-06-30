import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark', palette='deep')

def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

def categorize_hour(hr):
    if 1 <= hr < 12: 
        return "Pagi"
    elif 12 <= hr < 16:
        return "Siang"
    elif 16 <= hr <= 18:
        return "Sore"
    else:
        return "Malam" 

# Load dataset
data = load_data()
data['time_of_day'] = data['hr'].apply(categorize_hour)

# Sidebar for date selection
st.sidebar.image("dashboard/sepeda.jpg", use_column_width=True)
st.sidebar.title("Filter Data")
start_date = st.sidebar.date_input("Mulai Tanggal", min_value=data['dteday'].min(), max_value=data['dteday'].max(), value=data['dteday'].min())
end_date = st.sidebar.date_input("Akhir Tanggal", min_value=data['dteday'].min(), max_value=data['dteday'].max(), value=data['dteday'].max())

data_filtered = data[(data['dteday'] >= pd.Timestamp(start_date)) & (data['dteday'] <= pd.Timestamp(end_date))]

st.title("Analisis Penyewaan Sepeda 🚴")
st.subheader("Ringkasan Data")

col1, col2, col3 = st.columns(3)
col1.metric("Penyewa Kasual", data_filtered['casual'].sum())
col2.metric("Penyewa Terdaftar", data_filtered['registered'].sum())
col3.metric("Total Penyewaan", data_filtered['cnt'].sum())

# Penyewaan Berdasarkan Musim
st.subheader("Distribusi Penyewaan Berdasarkan Musim")
fig, ax = plt.subplots(figsize=(10,5))
sns.boxplot(x="season", y="cnt", data=data_filtered, palette="flare", ax=ax)
ax.set_xticklabels(['Spring', 'Summer', 'Fall', 'Winter'])
st.pyplot(fig)

# Penyewaan Berdasarkan Kondisi Cuaca
st.subheader("Distribusi Penyewaan Berdasarkan Kondisi Cuaca")
fig, ax = plt.subplots(figsize=(15,10))
sns.boxplot(x="weathersit", y="cnt", data=data_filtered, palette="viridis", ax=ax)
ax.set_xticklabels(["1", "2", "3", "4"])
legend_labels = [
    "1: Clear/Few clouds/Partly cloudy",
    "2: Mist + Cloudy/Mist + Broken clouds/Mist + Few clouds/Mist",
    "3: Light Snow/Light Rain + Thunderstorm/Scattered clouds/Light Rain + Scattered clouds",
    "4: Heavy Rain + Ice Pallets + Thunderstorm + Mist/Snow + Fog"
]
ax.legend(handles=ax.patches[:4], labels=legend_labels, title="Kategori Cuaca", loc="upper right", fontsize=7)
st.pyplot(fig)

# Korelasi Faktor Lingkungan dengan Penyewaan
st.subheader("Korelasi antara Faktor Lingkungan dan Penyewaan Sepeda")
fig, ax = plt.subplots(figsize=(10,5))
sns.heatmap(data_filtered[['temp', 'hum', 'windspeed', 'cnt']].corr(), annot=True, cmap="coolwarm", linewidths=0.5, ax=ax)
st.pyplot(fig)

# Penyewaan Berdasarkan Hari Kerja (Working Day) vs Akhir Pekan (Non-Working Day) vs Hari Libur (Holiday)
st.subheader("Penyewaan Sepeda: Hari Kerja vs Akhir Pekan vs Hari Libur")
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

sns.barplot(x="workingday", y="cnt", data=data_filtered, palette="tab20b", ax=axes[0], estimator=sum)
axes[0].set_xticklabels(["Non-Working Day", "Working Day"])
axes[0].set_title("Penyewaan Berdasarkan Hari Kerja (Working Day)")

sns.barplot(x="holiday", y="cnt", data=data_filtered, palette="tab20b", ax=axes[1], estimator=sum)
axes[1].set_xticklabels(["Non-Holiday", "Holiday"])
axes[1].set_title("Penyewaan Berdasarkan Hari Libur (Holiday)")

st.pyplot(fig)


# Tren Penyewaan Berdasarkan Waktu dalam Sehari
st.subheader("Rata-rata Penyewaan Sepeda Berdasarkan Waktu dalam Sehari")
time_of_day_counts = data_filtered.groupby("time_of_day")["cnt"].mean().reindex(["Pagi", "Siang", "Sore", "Malam"])
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x=time_of_day_counts.index, y=time_of_day_counts.values, palette="deep", ax=ax)
st.pyplot(fig)

# Tren Penyewaan Sepeda Harian
st.subheader("Tren Penyewaan Sepeda Harian")
fig, ax = plt.subplots(figsize=(20,8))
sns.pointplot(x="hr", y="cnt", data=data_filtered, hue='weekday', ax=ax)
ax.set_title("Tren Distribusi Penyewa Sepeda Berdasarkan Hari", fontsize=18)
legend = ax.legend(title="Kategori Hari", fontsize=12, title_fontsize=14, loc='upper left', bbox_to_anchor=(1, 1))
st.pyplot(fig)

st.caption("© 2025 Dashboard Penyewaan Sepeda")
