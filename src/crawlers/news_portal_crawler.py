# src/crawlers/news_portal_crawler.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def crawl_detik_news(total_pages=3):
    """
    Fungsi final untuk melakukan crawling berita dari Detik.com dari beberapa halaman.
    Selector sudah diperbaiki berdasarkan hasil debug.
    """
    base_url = "https://www.detik.com/search/searchall"
    search_query = "timnas indonesia piala dunia 2026"
    all_articles_data = [] # Menggunakan list untuk performa yang lebih baik

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for page in range(1, total_pages + 1):
        params = {
            'query': search_query,
            'sortby': 'time',
            'page': page
        }
        
        print(f"\n---> Mengambil data dari halaman {page}...")
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Gagal mengambil halaman {page}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        # Selector untuk kontainer artikel sudah benar: <article class="list-content__item">
        articles = soup.find_all('article', {'class': 'list-content__item'})
        
        if not articles:
            print(f"Tidak ada artikel ditemukan di halaman {page}. Berhenti.")
            break
        
        print(f"Ditemukan {len(articles)} kontainer artikel. Mulai mengekstrak data...")

        extracted_count = 0
        for article in articles:
            # === PERBAIKAN UTAMA DI SINI ===
            # Judul ada di dalam tag <h3> dengan class 'media__title'
            title_tag = article.find('h3', {'class': 'media__title'})
            # Kategori ada di dalam tag <h2> dengan class 'media__subtitle'
            category_tag = article.find('h2', {'class': 'media__subtitle'})
            # Tanggal ada di dalam div dengan class 'media__date'
            date_tag = article.find('div', {'class': 'media__date'})
            
            # Lewati jika salah satu elemen penting tidak ada
            if not all([title_tag, category_tag, date_tag]):
                continue

            # Ekstraksi data
            title = title_tag.get_text(strip=True)
            url_tag = title_tag.find('a')
            source_url = url_tag['href'] if url_tag else "Tidak ada URL"
            category = category_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            all_articles_data.append({
                'title': title,
                'publish_date': date_text,
                'crawl_timestamp': crawl_time,
                'author': 'Detik.com',
                'source': category, # Menggunakan sub-kanal (detikSumbagsel) sebagai source
                'category': 'Sepakbola', # Bisa di-hardcode atau diekstrak lebih lanjut
                'url': source_url,
                'source_type': 'news'
            })
            extracted_count += 1
        
        print(f"Berhasil mengekstrak {extracted_count} artikel dari halaman {page}.")
        time.sleep(1) 

    if not all_articles_data:
        return None

    # Konversi list of dictionary ke DataFrame di akhir, lebih efisien
    return pd.DataFrame(all_articles_data)

# Blok if __name__ == '__main__' tidak perlu diubah, biarkan seperti semula
if __name__ == '__main__':
    print("Mulai proses crawling berita Detik (testing)...")
    detik_df = crawl_detik_news(total_pages=2)
    
    if detik_df is not None and not detik_df.empty:
        output_path = 'data/raw/news_articles_detik_test.csv'
        detik_df.to_csv(output_path, index=False)
        print(f"\nBerhasil menyimpan {len(detik_df)} artikel ke {output_path}")
        print(f"\nContoh data:\n")
        print(detik_df.head())
    else:
        print("Proses crawling tidak menghasilkan data.")