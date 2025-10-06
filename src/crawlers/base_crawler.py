# src/crawlers/base_crawler.py

import httpx
from bs4 import BeautifulSoup

# Client httpx global yang akan digunakan oleh crawler yang aktif
CLIENT = httpx.AsyncClient(
    follow_redirects=True, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 1.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
    timeout=30.0
)

async def get_full_text(url: str, source: str) -> str:
    """
    Fungsi asinkron untuk mengambil teks lengkap dari URL artikel.
    Logika untuk Bola.net sudah dihapus.
    """
    try:
        response = await CLIENT.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if source == 'detik':
            body = soup.find('div', class_='detail__body-text')
            if body: 
                return ' '.join([p.get_text(strip=True) for p in body.find_all('p')])
        
        elif source == 'kompas':
            body = soup.find('div', class_='read__content')
            if body:
                for unwanted in body.select('.read__also, .ads-on-body, script, style, .kgnw-middle, .kompasidRec, .banner-300, .photo, .video, .twitter-tweet, iframe'):
                    unwanted.decompose()
                return body.get_text(strip=True, separator=' ')

        # Jika sumber tidak dikenal atau gagal, kembalikan pesan ini
        return "Teks lengkap tidak ditemukan."
    except Exception as e:
        print(f"   - Terjadi error saat memproses {url}: {e}")
        return f"Error: {e}"