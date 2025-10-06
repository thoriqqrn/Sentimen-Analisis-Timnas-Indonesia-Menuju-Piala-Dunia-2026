# src/crawlers/detik_crawler.py

import asyncio
from bs4 import BeautifulSoup
from .base_crawler import CLIENT, get_full_text # Import dari file base

async def crawl_detik(total_pages: int):
    """Crawler khusus untuk Detik.com."""
    print("\n[INFO] Memulai crawling Detik.com...")
    base_url = "https://www.detik.com/search/searchall"
    search_query = "timnas indonesia piala dunia 2026"
    tasks_metadata = []
    
    for page in range(1, total_pages + 1):
        try:
            await asyncio.sleep(0.5)
            params = {'query': search_query, 'sortby': 'time', 'page': page}
            response = await CLIENT.get(base_url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article', {'class': 'list-content__item'})
            
            for article in articles:
                title_tag = article.find('h3', {'class': 'media__title'})
                url = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else None
                if not url: continue
                
                tasks_metadata.append({
                    'title': title_tag.get_text(strip=True), 
                    'url': url, 
                    'publish_date': article.find('div', {'class': 'media__date'}).get_text(strip=True), 
                    'source': article.find('h2', {'class': 'media__subtitle'}).get_text(strip=True), 
                    'author': 'Detik.com', 
                    'full_text_coro': get_full_text(url, 'detik')
                })
        except Exception as e:
            print(f"  - Gagal mengambil daftar artikel Detik halaman {page}: {e}")
            
    print(f"[SUCCESS] Selesai mengambil metadata Detik.com, ditemukan {len(tasks_metadata)} artikel.")
    return tasks_metadata