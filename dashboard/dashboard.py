import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load the dataset
day_df = pd.read_csv('data/day.csv')
hour_df = pd.read_csv('data/hour.csv')

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
day_df['year'] = day_df['dteday'].dt.year
hour_df['year'] = hour_df['dteday'].dt.year

# Header
st.image("https://storage.googleapis.com/macrovector-acl-eu/previews/56224/preview_56224.jpg", width=700)
st.header('Analisis Dataset Bike Sharing :bike:')

# Sidebar
st.sidebar.image("https://dicoding-assets.sgp1.cdn.digitaloceanspaces.com/blog/wp-content/uploads/2014/12/dicoding-header-logo.png", width=300)
min_date = day_df['dteday'].min().date()
max_date = day_df['dteday'].max().date()

# Date range filter
start_date, end_date = st.sidebar.date_input(
    label='Pilih Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

filtered_day = day_df[(day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
filtered_hour = hour_df[(hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)]

todays_cnt = int(filtered_day['cnt'].iloc[-1])
yesterdays_cnt = int(filtered_day['cnt'].iloc[-2])

# Metric
st.sidebar.metric(
    label="Pertumbuhan harian pengguna",
    value=todays_cnt,
    delta=yesterdays_cnt
)

# Jumlah users
daily_users_data = filtered_day.groupby('dteday').agg({
    'casual': 'sum',
    'registered': 'sum',
    'cnt': 'sum'
}).reset_index()

st.subheader('Presentase Pengguna / Pelanggan')

col1, col2, col3 = st.columns(3)

def format_number(number):
    return f"{number:,}"

with col1:
    total_casual = daily_users_data.casual.sum()
    st.metric("Total Pelanggan Casual", value=format_number(total_casual))

with col2:
    total_registered = daily_users_data.registered.sum()
    st.metric("Total Pelanggan Registered", value=format_number(total_registered))

with col3:
    total_cnt = daily_users_data.cnt.sum()
    st.metric("Total Pelanggan", value=format_number(total_cnt))

# PLOT 1
user_counts_data = [total_casual, total_registered]

fig_pie, ax_pie = plt.subplots()
ax_pie.pie(user_counts_data, labels=['Casual', 'Registered'], explode=(0,0.05), autopct='%1.1f%%', startangle=320, colors=['#FFC01A', '#90CAFF'])
ax_pie.axis('equal')
ax_pie.set_title("Presentase (Casual vs Registered)")
st.pyplot(fig_pie)

# PLOT 2
st.subheader('Jumlah Penyewa Sepeda per Jam')

cluster_df = filtered_hour.groupby(['hr']).agg({
    'cnt':'sum'
}).reset_index()

# Plotting
fig_fh2, ax_fh2 = plt.subplots(figsize=(12, 6))
ax_fh2.plot(cluster_df['hr'], cluster_df['cnt'], marker='o', color="#90CAFF")
ax_fh2.set_ylabel("Jumlah Penyewa")
ax_fh2.set_xlabel("Waktu (jam)")
ax_fh2.set_title("Jumlah Penyewa per Jam")
ax_fh2.set_xticks(cluster_df['hr'])
ax_fh2.tick_params(axis='x', rotation=45)

for hour in [5, 10, 15, 20]:
    plt.axvline(x=hour, linestyle='--', color='black')

st.pyplot(fig_fh2)

with st.expander("Keterangan"):
    st.write("""
        Plot di atas adalah klasterisasi sederhana untuk membagi jam pelayanan Bike Sharing dalam beberapa kategori. Kategori yang digunakan adalah:

        - Jam sepi pengguna; Jam 0 atau 12 malam hingga jam 5 pagi
        - Jam sedang pengguna; Setelah jam 10 hingga 3 sore, lalu diikuti oleh jam 8 malam hingga sebelum jam 12 malam.
        - Jam ramai pengguna; Untuk jam sedang pengguna dari tabel diatas adalah jetelah jam 5 hingga jam 10 pagi, lalu diikuti oleh jam 3 sore hingga sebelum jam 8 malam.

        Asumsi yang bisa diambil dari klasterisasi tersebut adalah bahwa Bike Sharing ramai pengguna pada jam berangkat kerja dan saat pulang kerja. Pada siang hari, pengguna cenderung "standar" atau tidak terlalu ramai. Sedangkan pada saat larut malam hingga pagi saat masih istirahat, pengguna sangat sedikit.
    """)