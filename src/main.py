# src/main.py

import pandas as pd
from crawlers.news_portal_crawler import crawl_detik_news
from preprocessing.cleaner import clean_text, format_date
from analysis.word_frequency import calculate_word_frequency, plot_top_words
from analysis.sentiment_analyzer import translate_to_english, analyze_sentiment, plot_sentiment_distribution
# <-- IMPORT FUNGSI ANALISIS TREN BARU
from analysis.trend_analyzer import analyze_posts_over_time

def main():
    """
    Fungsi utama untuk menjalankan seluruh pipeline proyek.
    """
    print("=============================================")
    print("Memulai Pipeline Analisis Media Timnas 2026")
    print("=============================================")

    # Path file
    processed_data_path = 'data/processed/cleaned_data.csv'
    final_data_path = 'data/final/analysis_results.csv'
    
    # (Kita akan lewati crawling & preprocessing untuk fokus pada analisis)
    print("\n[INFO] Menggunakan data yang sudah diproses dari `data/processed/cleaned_data.csv`.")
    try:
        df_processed = pd.read_csv(processed_data_path)
    except FileNotFoundError:
        print(f"ERROR: File {processed_data_path} tidak ditemukan. Harap jalankan pipeline lengkap sekali lagi.")
        return

    # --- TAHAP ANALISIS & VISUALISASI ---
    print("\n[ANALISIS] Memulai proses analisis data...")
    
    # 3.1 Analisis Frekuensi Kata
    print("   - Menganalisis frekuensi kata...")
    top_words = calculate_word_frequency(df_processed['cleaned_title'])
    plot_top_words(top_words, 'reports/figures/top_words_barchart.png')
        
    # 3.2 Analisis Sentimen
    print("   - Menganalisis sentimen...")
    df_final = df_processed.copy() # Buat salinan untuk data final
    df_final['translated_title'] = df_final['cleaned_title'].apply(translate_to_english)
    df_final['sentiment'] = df_final['translated_title'].apply(analyze_sentiment)
    sentiment_distribution = df_final['sentiment'].value_counts()
    print("\n   Distribusi Sentimen:")
    print(sentiment_distribution)
    plot_sentiment_distribution(sentiment_distribution, 'reports/figures/sentiment_pie_chart.png')
    
    # 3.3 Analisis Tren Waktu
    print("\n   - Menganalisis tren pemberitaan per hari...")
    # Pastikan kolom tanggal sudah dalam format datetime untuk analisis
    df_final['formatted_date'] = pd.to_datetime(df_final['formatted_date']) 
    analyze_posts_over_time(df_final)

    # Simpan hasil akhir yang sudah lengkap
    df_final.to_csv(final_data_path, index=False)
    print(f"\n   Data dengan hasil analisis lengkap disimpan ke: {final_data_path}")
    
    print("\n=============================================")
    print("Pipeline Selesai.")
    print("=============================================")

if __name__ == '__main__':
    main()