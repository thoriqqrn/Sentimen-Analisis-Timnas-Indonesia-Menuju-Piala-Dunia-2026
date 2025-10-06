# src/crawlers/kompas_crawler.py

import asyncio
from bs4 import BeautifulSoup
from .base_crawler import CLIENT, get_full_text

async def crawl_kompas(total_pages: int):
    """Crawler khusus untuk Kompas.com."""
    print("\n[INFO] Memulai crawling Kompas.com...")
    base_url = "https://www.kompas.com/tag/timnas-indonesia?sort=desc"
    tasks_metadata = []
    
    for page in range(1, total_pages + 1):
        try:
            await asyncio.sleep(0.5)
            response = await CLIENT.get(f"{base_url}&page={page}")
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='articleItem')
            
            for article in articles:
                title_tag = article.find('h2', class_='articleTitle')
                link_tag = article.find('a', class_='article-link')
                date_tag = article.find('div', class_='articlePost-date')
                if not all([title_tag, link_tag, date_tag]): continue
                
                url = link_tag['href']
                tasks_metadata.append({
                    'title': title_tag.get_text(strip=True), 
                    'url': url, 
                    'publish_date': date_tag.get_text(strip=True), 
                    'source': 'Kompas.com', 
                    'author': 'Kompas.com', 
                    'full_text_coro': get_full_text(url, 'kompas')
                })
        except Exception as e:
            print(f"  - Gagal mengambil daftar artikel Kompas halaman {page}: {e}")
            
    print(f"[SUCCESS] Selesai mengambil metadata Kompas.com, ditemukan {len(tasks_metadata)} artikel.")
    return tasks_metadata