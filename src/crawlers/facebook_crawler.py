# src/crawlers/facebook_crawler.py (Versi Selenium)

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

def get_selenium_driver():
    """Membuat instance driver Selenium baru."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # JALANKAN DENGAN BROWSER TERLIHAT DULU UNTUK DEBUG
    options.add_argument("--disable-notifications") # Matikan notifikasi pop-up
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_facebook(driver):
    """Fungsi untuk login ke Facebook."""
    fb_email = os.getenv("FB_EMAIL")
    fb_password = os.getenv("FB_PASSWORD")

    if not fb_email or not fb_password:
        print("[ERROR] Email atau Password Facebook tidak ditemukan di file .env")
        return False
        
    print("[INFO] Membuka halaman login Facebook...")
    driver.get("https://www.facebook.com")
    
    # Tunggu halaman login dimuat dan tolak cookie jika ada
    try:
        reject_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Tolak') or contains(., 'Decline')]"))
        )
        reject_button.click()
        print("[INFO] Tombol cookie ditolak.")
    except Exception as e:
        print("[INFO] Tidak ada dialog cookie, atau gagal ditolak. Melanjutkan...")

    try:
        print("[INFO] Memasukkan email dan password...")
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "pass")
        
        email_input.send_keys(fb_email)
        password_input.send_keys(fb_password)
        password_input.send_keys(Keys.RETURN)
        
        # Tunggu hingga login berhasil (misal, dengan menunggu elemen halaman utama muncul)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Beranda']"))
        )
        print("[SUCCESS] Login Facebook berhasil.")
        return True
    except Exception as e:
        print(f"[ERROR] Gagal login ke Facebook: {e}")
        return False

def crawl_facebook(target_id, scroll_count=3):
    """
    Mengambil postingan dari halaman Facebook menggunakan Selenium.
    """
    driver = get_selenium_driver()
    all_posts_data = []
    
    try:
        if not login_to_facebook(driver):
            return None # Hentikan jika login gagal

        target_url = f"https://www.facebook.com/{target_id}"
        print(f"\n[INFO] Mengunjungi halaman target: {target_url}")
        driver.get(target_url)
        time.sleep(5) # Beri waktu halaman untuk memuat postingan awal

        print(f"[INFO] Mulai scroll halaman sebanyak {scroll_count} kali...")
        for _ in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Tunggu konten baru dimuat

        # Setelah scroll, ambil HTML halaman dan proses dengan BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Selector ini lebih umum untuk postingan di timeline
        posts = soup.select('div[role="article"]')
        
        print(f"[INFO] Ditemukan {len(posts)} kontainer postingan. Mulai mengekstrak data...")
        
        for post in posts:
            post_text = post.get_text(separator=' ', strip=True)
            
            # Filter postingan yang relevan
            if 'timnas' in post_text.lower() or 'indonesia' in post_text.lower():
                # Cari link ke postingan individual (selector ini mungkin perlu disesuaikan)
                link_tag = post.find('a', href=lambda href: href and '/posts/' in href)
                post_url = "https://www.facebook.com" + link_tag['href'] if link_tag else target_url
                
                # Cari timestamp (selector ini sangat tentatif)
                time_tag = post.find('a', href=lambda href: href and '/posts/' in href and not href.endswith('/'))
                post_time_text = time_tag.get_text(strip=True) if time_tag else "Waktu tidak ditemukan"
                
                all_posts_data.append({
                    'source_type': 'facebook',
                    'source': target_id,
                    'author': target_id,
                    'publish_date': post_time_text, # Ini masih format mentah
                    'full_text': post_text,
                    'url': post_url,
                    # Likes/Comments/Shares lebih sulit didapat dengan cara ini, kita set 0
                    'likes': 0, 'comments': 0, 'shares': 0
                })

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat crawling Facebook: {e}")
    finally:
        print("[INFO] Menutup browser Selenium...")
        driver.quit()

    print(f"[SUCCESS] Selesai crawling Facebook, ditemukan {len(all_posts_data)} postingan yang relevan.")
    return pd.DataFrame(all_posts_data)