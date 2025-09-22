# dashboard/app.py

import streamlit as st
import pandas as pd
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Analisis Media Timnas",
    page_icon="⚽",
    layout="wide"
)

# --- FUNGSI UNTUK MEMUAT DATA ---
# Menggunakan cache agar data tidak perlu dimuat ulang setiap kali ada interaksi
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan di path: {path}. Pastikan pipeline utama (main.py) sudah dijalankan.")
        return None

# --- JUDUL DASHBOARD ---
st.title("⚽ Dashboard Analisis Media: Timnas Indonesia Menuju Piala Dunia 2026")
st.write("Dashboard ini menampilkan hasil analisis dari berita online terkait Timnas Indonesia.")

# --- MEMUAT DATA ---
final_data_path = 'data/final/analysis_results.csv'
df = load_data(final_data_path)

if df is not None:
    # --- RINGKASAN DATA ---
    st.header("Ringkasan Analisis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Artikel Dianalisis", f"{len(df)}")
    
    # Hitung sentimen
    sentiment_counts = df['sentiment'].value_counts()
    col2.metric("Sentimen Paling Dominan", f"{sentiment_counts.index[0].capitalize()}", f"{sentiment_counts.iloc[0]} Artikel")
    
    # Ambil berita terbaru
    df['formatted_date'] = pd.to_datetime(df['formatted_date'])
    latest_news_date = df['formatted_date'].max().strftime('%d %B %Y')
    col3.metric("Berita Terbaru Tanggal", latest_news_date)

    # --- VISUALISASI UTAMA ---
    st.header("Visualisasi Hasil Analisis")

    # Membuat dua kolom untuk visualisasi
    vis_col1, vis_col2 = st.columns(2)

    with vis_col1:
        st.subheader("Distribusi Sentimen")
        try:
            sentiment_pie_chart = Image.open('reports/figures/sentiment_pie_chart.png')
            st.image(sentiment_pie_chart, caption='Distribusi sentimen dari seluruh judul berita.', use_column_width=True)
        except FileNotFoundError:
            st.warning("Gambar pie chart sentimen tidak ditemukan. Jalankan `main.py` untuk membuatnya.")

    with vis_col2:
        st.subheader("Top 15 Kata yang Sering Muncul")
        try:
            top_words_chart = Image.open('reports/figures/top_words_barchart.png')
            st.image(top_words_chart, caption='Kata-kata yang paling sering muncul di judul berita (setelah dibersihkan).', use_column_width=True)
        except FileNotFoundError:
            st.warning("Gambar bar chart frekuensi kata tidak ditemukan. Jalankan `main.py` untuk membuatnya.")

    st.subheader("Tren Pemberitaan per Hari")
    try:
        trend_chart = Image.open('reports/figures/posts_over_time_line_chart.png')
        st.image(trend_chart, caption='Jumlah artikel berita yang dipublikasikan setiap harinya.', use_column_width=True)
    except FileNotFoundError:
        st.warning("Gambar line chart tren waktu tidak ditemukan. Jalankan `main.py` untuk membuatnya.")

    # --- TAMPILKAN DATA MENTAH (INTERAKTIF) ---
    st.header("Eksplorasi Data Hasil Analisis")
    if st.checkbox("Tampilkan data lengkap hasil analisis"):
        st.dataframe(df)