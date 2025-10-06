# run_preprocessing.py (Versi Final untuk Berita + YouTube)

import pandas as pd
import os
import glob
from src.preprocessing.cleaner import clean_text, format_date

def main():
    print("======================================================")
    print("🧹 MEMULAI STASIUN 2: PREPROCESSING (BERITA + YOUTUBE) 🧹")
    print("======================================================")
    
    # Gabungkan SEMUA file .csv dari folder data/raw
    all_raw_files = glob.glob('data/raw/*.csv')
    
    if not all_raw_files:
        print("[ERROR] Tidak ada file data mentah di 'data/raw/'. Jalankan script crawling terlebih dahulu.")
        return

    df_list = []
    for f in all_raw_files:
        print(f"[INFO] Membaca data dari '{f}'...")
        df_list.append(pd.read_csv(f))

    df = pd.concat(df_list, ignore_index=True)
    
    # Hapus duplikat berdasarkan teks lengkap untuk mencegah data ganda
    df.drop_duplicates(subset=['full_text'], inplace=True, keep='first')
    print(f"\n[INFO] Total {len(df)} data unik digabungkan.")

    # Standarisasi kolom
    print("[INFO] Memulai pembersihan teks dan format tanggal...")
    if 'title' not in df.columns:
        df['title'] = df['full_text'].str[:70] + '...'
    df['title'].fillna(df['full_text'].str[:70] + '...', inplace=True)
    
    df['cleaned_full_text'] = df['full_text'].apply(clean_text)
    df['formatted_date'] = df['publish_date'].apply(format_date)
    
    # Hapus baris yang datanya tidak lengkap setelah diproses
    df.dropna(subset=['formatted_date', 'full_text'], inplace=True)

    output_path = 'data/processed/master_cleaned_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Dataset master bersih dengan {len(df)} baris data disimpan ke '{output_path}'.")
    print("\n✅ Stasiun Preprocessing Selesai.")

if __name__ == '__main__':
    main()