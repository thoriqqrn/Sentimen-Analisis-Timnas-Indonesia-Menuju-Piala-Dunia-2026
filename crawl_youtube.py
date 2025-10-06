# crawl_youtube.py

import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm
import pandas as pd
from langdetect import detect, LangDetectException
from dotenv import load_dotenv

# Muat variabel dari file .env (termasuk YT_API_KEY)
load_dotenv()

# ---------- KONFIGURASI CRAWLING YOUTUBE ----------
# Anda bisa mengubah semua pengaturan di sini
OUTPUT_CSV = "data/raw/youtube_comments_raw.csv" # Simpan di folder data/raw
QUERIES = [
    "Timnas Indonesia Kualifikasi Piala Dunia 2026",
    "Indonesia vs Irak Kualifikasi",
    "Highlight Timnas Indonesia",
    "STY interview timnas",
    "Garuda di Dada"
]
MAX_VIDEOS_PER_QUERY = 50         # Ambil 10 video teratas dari setiap pencarian
MAX_COMMENTS_PER_VIDEO = 200      # Ambil 200 komentar teratas dari setiap video
FILTER_INDONESIAN = True          # Hanya ambil komentar berbahasa Indonesia
# ---------------------------------------------------

def get_youtube_service():
    """Membuat dan mengembalikan service object untuk YouTube API."""
    api_key = os.getenv("YT_API_KEY")
    if not api_key:
        raise ValueError("YT_API_KEY tidak ditemukan di file .env. Harap tambahkan API Key Anda.")
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)

def search_videos(yt_service, query, max_results):
    """Mencari video berdasarkan query."""
    print(f"\n[INFO] Mencari video untuk query: '{query}'...")
    videos = []
    try:
        response = yt_service.search().list(
            q=query, part="id,snippet", type="video", maxResults=max_results,
            relevanceLanguage="id", regionCode="ID"
        ).execute()
        for item in response.get("items", []):
            videos.append({
                "videoId": item["id"]["videoId"],
                "videoTitle": item["snippet"]["title"],
            })
        print(f"   - Ditemukan {len(videos)} video.")
    except HttpError as e:
        print(f"   - ERROR saat mencari video: {e}")
    return videos

def fetch_comments_for_video(yt_service, video_id, max_comments):
    """Mengambil komentar dari satu video."""
    comments = []
    next_page_token = None
    fetched_count = 0
    
    while True:
        try:
            response = yt_service.commentThreads().list(
                part="snippet", videoId=video_id, maxResults=100,
                pageToken=next_page_token, textFormat="plainText"
            ).execute()
        except HttpError as e:
            # Jika komentar dinonaktifkan, lewati video ini
            if "commentsDisabled" in str(e):
                print(f"   - Komentar dinonaktifkan untuk video {video_id}. Melewati.")
                break
            print(f"   - ERROR saat mengambil komentar: {e}")
            break # Hentikan jika ada error lain

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            
            text = comment.get("textDisplay", "")
            # Lakukan filter bahasa di sini
            if FILTER_INDONESIAN:
                try:
                    if detect(text) != "id":
                        continue
                except LangDetectException:
                    continue # Lewati teks yang terlalu pendek untuk dideteksi
            
            comments.append({
                'source_type': 'youtube',
                'source': comment.get('authorChannelUrl', 'N/A'),
                'author': comment.get('authorDisplayName', 'N/A'),
                'publish_date': comment.get('publishedAt'),
                'full_text': text,
                'likes': comment.get('likeCount', 0),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': f"Komentar di video: {video_id}" # Judul placeholder
            })
            fetched_count += 1
            if fetched_count >= max_comments:
                break
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token or fetched_count >= max_comments:
            break
            
    return comments

def main():
    """Fungsi utama untuk menjalankan pipeline crawling YouTube."""
    print("=============================================")
    print("🚀 MEMULAI CRAWLING YOUTUBE (OPINI PUBLIK) 🚀")
    print("=============================================")
    os.makedirs('data/raw', exist_ok=True)
    
    try:
        yt_service = get_youtube_service()
    except ValueError as e:
        print(f"[FATAL ERROR] {e}")
        return

    all_new_comments = []
    
    # Cari video dari semua query
    all_videos = []
    for query in QUERIES:
        all_videos.extend(search_videos(yt_service, query, MAX_VIDEOS_PER_QUERY))
        time.sleep(1) # Jeda antar pencarian

    # Hapus duplikat video yang mungkin ditemukan dari query berbeda
    unique_videos = list({v['videoId']:v for v in all_videos}.values())
    print(f"\n[INFO] Total video unik yang akan di-crawl: {len(unique_videos)}")

    # Ambil komentar dari setiap video unik
    for video in tqdm(unique_videos, desc="Mengambil Komentar Video"):
        comments = fetch_comments_for_video(yt_service, video['videoId'], MAX_COMMENTS_PER_VIDEO)
        all_new_comments.extend(comments)
        time.sleep(1) # Jeda sopan antar video

    if all_new_comments:
        df_youtube = pd.DataFrame(all_new_comments)
        
        # Simpan atau tambahkan data baru ke file CSV
        if os.path.exists(OUTPUT_CSV):
            print(f"\n[INFO] Menambahkan {len(df_youtube)} komentar baru ke file yang ada...")
            df_youtube.to_csv(OUTPUT_CSV, mode='a', index=False, header=False)
        else:
            print(f"\n[INFO] Membuat file baru dan menyimpan {len(df_youtube)} komentar...")
            df_youtube.to_csv(OUTPUT_CSV, mode='w', index=False, header=True)
            
        print(f"[SUCCESS] Proses selesai. Data disimpan di '{OUTPUT_CSV}'.")
    else:
        print("\n[INFO] Tidak ada komentar baru yang ditemukan.")
        
    print("\n✅ Crawling YouTube Selesai.")

if __name__ == '__main__':
    main()