# src/analysis/trend_analyzer.py

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def analyze_posts_over_time(df, date_column='formatted_date'):
    """
    Menganalisis dan memvisualisasikan jumlah postingan per hari.
    
    Args:
        df (pd.DataFrame): DataFrame yang berisi data bersih.
        date_column (str): Nama kolom yang berisi tanggal (sudah dalam format datetime).
    """
    # Pastikan kolom tanggal adalah tipe datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Hitung jumlah berita per hari
    # Kita set kolom tanggal sebagai index, lalu hitung jumlah (count) per hari ('D')
    posts_per_day = df.set_index(date_column).resample('D').size()
    
    # Membuat plot
    plt.figure(figsize=(15, 7))
    plt.plot(posts_per_day.index, posts_per_day.values, marker='o', linestyle='-')
    
    # Mempercantik plot
    plt.title('Tren Jumlah Pemberitaan Timnas per Hari', fontsize=16)
    plt.xlabel('Tanggal', fontsize=12)
    plt.ylabel('Jumlah Berita', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Mengatur format tanggal di sumbu-x agar lebih mudah dibaca
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Simpan plot ke file
    save_path = 'reports/figures/posts_over_time_line_chart.png'
    plt.savefig(save_path)
    print(f"Grafik tren pemberitaan disimpan di: {save_path}")
    plt.close()
    
    return posts_per_day