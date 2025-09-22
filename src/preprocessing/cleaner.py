# src/preprocessing/cleaner.py

import re
import pandas as pd
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Buat instance stopword remover (hanya sekali agar efisien)
factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()

def clean_text(text):
    """
    Fungsi untuk membersihkan teks:
    1. Lowercase
    2. Hapus URL
    3. Hapus angka
    4. Hapus tanda baca
    5. Hapus spasi berlebih
    6. Hapus stopwords
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase
    text = text.lower()
    # 2. Hapus URL
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # 3. Hapus angka
    text = re.sub(r'\d+', '', text)
    # 4. Hapus tanda baca
    text = re.sub(r'[^\w\s]', '', text)
    # 5. Hapus spasi berlebih
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    # 6. Hapus stopwords
    text = stopword_remover.remove(text)
    
    return text

def format_date(date_string):
    """
    Fungsi untuk mengubah format tanggal dari 'Kamis, 17 Jul 2025 20:00 WIB'
    menjadi format standar 'YYYY-MM-DD HH:MM:SS'.
    """
    # Mapping bulan Indonesia ke angka
    month_map = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'mei': '05', 'jun': '06',
        'jul': '07', 'agu': '08', 'sep': '09', 'okt': '10', 'nov': '11', 'des': '12'
    }
    
    try:
        parts = date_string.lower().split() # e.g., ['kamis,', '17', 'jul', '2025', '20:00', 'wib']
        day = parts[1]
        month = month_map[parts[2]]
        year = parts[3]
        time = parts[4]
        
        return f"{year}-{month}-{day} {time}:00"
    except (IndexError, KeyError):
        # Jika format tidak sesuai, kembalikan None atau tanggal default
        return None