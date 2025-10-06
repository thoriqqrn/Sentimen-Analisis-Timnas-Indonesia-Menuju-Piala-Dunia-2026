# src/main.py (Perbaikan Final untuk Argumen Facebook)

import pandas as pd
import os
import asyncio
# Import semua crawler
from crawlers.detik_crawler import crawl_detik
from crawlers.kompas_crawler import crawl_kompas
from crawlers.bola_crawler import crawl_bola
from crawlers.facebook_crawler import crawl_facebook
# from crawlers.twitter_crawler import crawl_twitter # Kita biarkan import-nya di sini
# Import semua utilitas
from preprocessing.cleaner import clean_text, format_date
from analysis.sentiment_analyzer import translate_to_english, analyze_sentiment

async def run_news_crawlers():
    # Fungsi ini sudah benar, tidak perlu diubah
    print("\n[INFO] Menjalankan crawler portal berita secara paralel...")
    metadata_tasks = [crawl_detik(total_pages=70), crawl_kompas(total_pages=70), crawl_bola(total_pages=1)]
    results_nested_metadata = await asyncio.gather(*metadata_tasks)
    all_articles_metadata = [item for sublist in results_nested_metadata for item in sublist]
    print(f"\n[INFO] Metadata dari {len(all_articles_metadata)} artikel berita berhasil diambil. Mengambil teks lengkap...")
    CONCURRENT_LIMIT = 5
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    async def fetch_full_text_with_limit(task):
        async with semaphore:
            await asyncio.sleep(1) 
            full_text = await task.pop('full_text_coro')
            task['full_text'] = full_text
            return task
    full_article_tasks = [fetch_full_text_with_limit(task) for task in all_articles_metadata]
    results = await asyncio.gather(*full_article_tasks, return_exceptions=True)
    final_articles = [res for res in results if not isinstance(res, Exception)]
    print(f"[INFO] Selesai mengambil teks lengkap berita. Berhasil: {len(final_articles)} artikel.")
    return pd.DataFrame(final_articles)

def main():
    """Pipeline final yang menggabungkan data dari Berita & Facebook."""
    print("======================================================")
    print("Memulai Pipeline Gabungan Timnas 2026")
    print("======================================================")

    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/final', exist_ok=True)
    final_data_path = 'data/final/analysis_results.csv'

    # --- TAHAP 1: DATA COLLECTION ---
    df_news = asyncio.run(run_news_crawlers())
    
    # --- PERBAIKAN DI SINI ---
    df_facebook = crawl_facebook(target_id='timnasindonesia', scroll_count=50) 
    # -------------------------
    
    # Untuk sementara kita nonaktifkan Twitter
    df_twitter = pd.DataFrame() 

    df_crawled = pd.concat([df_news, df_facebook, df_twitter], ignore_index=True)

    if df_crawled is None or df_crawled.empty:
        print("\n[ERROR] GAGAL: Tidak ada data yang berhasil di-crawl dari sumber manapun.")
        return

    df_crawled.to_csv('data/raw/combined_raw_data.csv', index=False)
    print(f"\n[INFO] Total {len(df_crawled)} data dari semua sumber berhasil digabungkan.")

    # --- TAHAP 2 & 3 (Tidak ada perubahan) ---
    print(f"\n[PREPROCESSING] Memulai...")
    if 'title' not in df_crawled.columns:
        df_crawled['title'] = df_crawled['full_text'].str[:70] + '...'
    df_crawled['title'].fillna(df_crawled['full_text'].str[:70] + '...', inplace=True)
    df_crawled['cleaned_title'] = df_crawled['title'].apply(clean_text)
    df_crawled['cleaned_full_text'] = df_crawled['full_text'].apply(clean_text)
    df_crawled['formatted_date'] = df_crawled['publish_date'].apply(format_date)
    df_crawled.dropna(subset=['formatted_date', 'full_text'], inplace=True)
    df_final = df_crawled.copy()
    print("\n[ANALISIS] Memulai proses analisis sentimen...")
    print("   - Menerjemahkan ringkasan teks...")
    df_final['text_for_translation'] = df_final['cleaned_full_text'].str[:4900]
    df_final['translated_text'] = df_final['text_for_translation'].apply(translate_to_english)
    df_final['sentiment'] = df_final['translated_text'].apply(analyze_sentiment)
    df_final.to_csv(final_data_path, index=False)
    print(f"\n[SUKSES] Data gabungan dari semua sumber disimpan ke: '{final_data_path}'.")
    
    print("\n=============================================")
    print("Pipeline Selesai.")
    print("Jalankan dashboard dengan: streamlit run dashboard/app.py")
    print("=============================================")

if __name__ == '__main__':
    main()