# src/preprocessing/cleaner.py (Versi Final Lengkap)

import re
from datetime import datetime, timedelta
import pandas as pd
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Inisialisasi stopword remover
try:
    factory = StopWordRemoverFactory()
    stopword_remover = factory.create_stop_word_remover()
except Exception as e:
    print(f"WARNING: Gagal inisialisasi Sastrawi. Stopword removal dilewati. Error: {e}")
    stopword_remover = None

def clean_text(text):
    # Fungsi ini sudah solid
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    if stopword_remover:
        try:
            text = stopword_remover.remove(text)
        except:
            pass
    return text

def format_date(date_input):
    """
    Fungsi format tanggal final yang bisa menangani SEMUA format yang kita temui.
    """
    if pd.isna(date_input):
        return None
        
    # Langsung proses jika input sudah berupa objek datetime
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y-%m-%d %H:%M:%S')

    if not isinstance(date_input, str): 
        return None

    # --- PERBAIKAN UTAMA: Tangani format ISO 8601 dari YouTube ---
    # Format ini sangat umum, jadi kita prioritaskan
    try:
        # pd.to_datetime sangat pintar mengenali format ini
        dt_object = pd.to_datetime(date_input)
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, pd.errors.ParserError):
        # Jika bukan format ISO, lanjut ke logika berikutnya
        pass

    now = datetime.now()
    date_string = date_input.lower().strip()
    
    # Logika format relatif
    try:
        if ('jam' in date_string or 'hour' in date_string) and 'lalu' in date_string:
            hours_ago = int(re.search(r'(\d+)', date_string).group(1))
            return (now - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
        if ('menit' in date_string or 'minute' in date_string) and 'lalu' in date_string:
            minutes_ago = int(re.search(r'(\d+)', date_string).group(1))
            return (now - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
        if 'kemarin' in date_string:
            return (now - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        if ('hari' in date_string or 'day' in date_string) and 'lalu' in date_string:
            days_ago = int(re.search(r'(\d+)', date_string).group(1))
            return (now - timedelta(days=days_ago)).strftime('%Y-%m-%d 00:00:00')
    except: pass

    # Logika format absolut "manusia"
    month_map = {'januari': '01', 'februari': '02', 'maret': '03', 'april': '04', 'mei': '05', 'juni': '06','juli': '07', 'agustus': '08', 'september': '09', 'oktober': '10', 'november': '11', 'desember': '12','jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'mei': '05', 'jun': '06','jul': '07', 'agu': '08', 'sep': '09', 'okt': '10', 'nov': '11', 'des': '12'}
    
    try: # Format Detik
        parts = date_string.replace(',', '').split()
        if 'wib' in parts and len(parts) >= 5:
            day, month_str, year, time = parts[1], parts[2], parts[3], parts[4]
            return f"{year}-{month_map[month_str]}-{day} {time}:00"
    except: pass
    
    try: # Format Kompas
        parts = date_string.split()
        if len(parts) == 3 and parts[1] in month_map:
            day, month_str, year = parts[0].zfill(2), parts[1], parts[2]
            return f"{year}-{month_map[month_str]}-{day} 00:00:00"
    except: pass
    
    try: # Format Bola.net
        date_part, time_part = date_string.split(',')
        time = time_part.strip().split()[0]
        day, month_str, year = date_part.split()
        return f"{year}-{month_map[month_str]}-{day.zfill(2)} {time}:00"
    except: pass

    print(f"  - WARNING: Gagal memformat tanggal: '{date_input}'")
    return None