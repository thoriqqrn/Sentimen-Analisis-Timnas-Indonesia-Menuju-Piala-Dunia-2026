# crawl_twitter_only.py

import pandas as pd
import os
from datetime import datetime, timedelta
from src.crawlers.twitter_crawler import crawl_twitter

def main():
    print("=============================================")
    print("🚀 MEMULAI CRAWLING TWITTER (OPINI PUBLIK) 🚀")
    print("=============================================")
    os.makedirs('data/raw', exist_ok=True)

    # --- KONFIGURASI CRAWLING ---
    
    # 1. Tentukan daftar kata kunci Anda
    # Ini memenuhi permintaan dosen Anda untuk multiple keywords.
    KEYWORD_LIST = [
        "timnas indonesia",
        "skuad garuda",
        "shin tae yong",
        "STY",
        "kualifikasi piala dunia"
    ]

    # 2. Tentukan rentang waktu (misal: 1 bulan terakhir)
    END_DATE = datetime.now().strftime('%Y-%m-%d')
    START_DATE = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # 3. Tentukan batas jumlah tweet per kata kunci
    MAX_TWEETS_PER_KEYWORD = 200 # Total akan menjadi 5 * 200 = 1000 tweet

    # --- Menjalankan Crawler ---
    df_twitter = crawl_twitter(
        keywords=KEYWORD_LIST,
        start_date=START_DATE,
        end_date=END_DATE,
        max_tweets_per_keyword=MAX_TWEETS_PER_KEYWORD
    )

    if df_twitter is not None and not df_twitter.empty:
        output_path = 'data/raw/twitter_posts_raw.csv'
        # Gunakan mode 'append' agar bisa menambah data di lain waktu
        df_twitter.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))
        print(f"[SUCCESS] {len(df_twitter)} tweet baru disimpan/ditambahkan ke '{output_path}'.")
    else:
        print("[FAILED] Tidak ada data yang berhasil diambil dari Twitter.")

    print("\n✅ Crawling Twitter Selesai.")

if __name__ == '__main__':
    main()