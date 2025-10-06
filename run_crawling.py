# run_crawling.py

import pandas as pd
import asyncio
import os
from src.crawlers.detik_crawler import crawl_detik
from src.crawlers.kompas_crawler import crawl_kompas
from src.crawlers.bola_crawler import crawl_bola
# from src.crawlers.facebook_crawler import crawl_facebook

async def main():
    print("=============================================")
    print("🚀 MEMULAI STASIUN 1: CRAWLING DATA MENTAH 🚀")
    print("=============================================")
    
    os.makedirs('data/raw', exist_ok=True)

    # --- CRAWLING PORTAL BERITA ---
    print("\n[INFO] Menjalankan crawler portal berita...")
    # Anda bisa mengatur `total_pages` di sini, misal 5 halaman per sumber
    news_tasks = [
        crawl_detik(total_pages=70),
        crawl_kompas(total_pages=70),
        crawl_bola(total_pages=5)
    ]
    results_nested = await asyncio.gather(*news_tasks)
    all_articles = [item for sublist in results_nested for item in sublist if sublist]
    df_news = pd.DataFrame(all_articles)

    if not df_news.empty:
        # Simpan atau tambahkan ke file yang ada (mode 'a' = append)
        output_path = 'data/raw/news_articles_raw.csv'
        df_news.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))
        print(f"\n[SUCCESS] {len(df_news)} artikel berita baru disimpan/ditambahkan ke '{output_path}'.")

    # --- CRAWLING FACEBOOK ---
    # `scroll_count` menentukan berapa banyak data baru yang diambil
    # df_facebook = crawl_facebook(target_id='timnasindonesia', scroll_count=3)
    # if df_facebook is not None and not df_facebook.empty:
    #     output_path = 'data/raw/facebook_posts_raw.csv'
    #     df_facebook.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))
    #     print(f"[SUCCESS] {len(df_facebook)} postingan Facebook baru disimpan/ditambahkan ke '{output_path}'.")

    print("\n✅ Stasiun Crawling Selesai.")

if __name__ == '__main__':
    # Untuk menjalankan fungsi asinkron
    asyncio.run(main())