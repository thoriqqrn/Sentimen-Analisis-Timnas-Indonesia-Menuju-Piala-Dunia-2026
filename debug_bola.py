# debug_bola.py

import asyncio
from src.crawlers.bola_crawler import crawl_bola

async def test_bola_crawler():
    """
    Fungsi ini HANYA akan menjalankan crawler Bola.net
    dan mencetak hasilnya langsung ke terminal.
    """
    print("--- MEMULAI TES KHUSUS BOLA.NET ---")
    
    # Kita panggil crawler Bola.net untuk mengambil metadata
    # total_pages di sini tidak begitu penting karena Google News hanya punya 1 halaman hasil
    list_of_articles_metadata = await crawl_bola(total_pages=1)
    
    if not list_of_articles_metadata:
        print("\n[HASIL TES] GAGAL: Tidak ada metadata artikel yang berhasil diambil.")
        return

    print(f"\n[HASIL TES] BERHASIL: Ditemukan {len(list_of_articles_metadata)} artikel.")
    print("--- Mencoba mengambil teks lengkap dari 3 artikel pertama... ---")
    
    # Kita akan coba eksekusi 'get_full_text' untuk 3 artikel pertama
    tasks_to_run = [task.pop('full_text_coro') for task in list_of_articles_metadata[:3]]
    
    # Jalankan pengambilan teks
    full_texts = await asyncio.gather(*tasks_to_run)
    
    # Cetak hasilnya
    for i, text in enumerate(full_texts):
        article_title = list_of_articles_metadata[i]['title']
        print(f"\n--- Artikel #{i+1}: {article_title} ---")
        if "Error:" in text or "tidak ditemukan" in text:
            print(f"[GAGAL] Pesan: {text}")
        else:
            print(f"[BERHASIL] Teks ditemukan (potongan): {text[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_bola_crawler())