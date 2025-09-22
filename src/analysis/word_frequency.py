# src/analysis/word_frequency.py

import pandas as pd
from collections import Counter

# ==================== PERBAIKAN DI SINI ====================
import matplotlib
matplotlib.use('Agg') # <-- BARIS PENTING 1: Set backend SEBELUM pyplot di-import
import matplotlib.pyplot as plt # <-- BARIS PENTING 2: Import pyplot SETELAH backend di-set
# =========================================================

def calculate_word_frequency(series_text):
    """
    Menghitung frekuensi setiap kata dari sebuah Series pandas.
    """
    full_text = ' '.join(series_text.dropna())
    words = full_text.split()
    word_counts = Counter(words)
    return word_counts.most_common(15)

def plot_top_words(word_counts, save_path):
    """
    Membuat bar chart dari frekuensi kata dan menyimpannya ke file.
    """
    if not word_counts:
        print("Tidak ada data frekuensi kata untuk di-plot.")
        return
        
    words, counts = zip(*word_counts)
    
    plt.figure(figsize=(12, 8))
    plt.barh(words, counts, color='skyblue')
    plt.xlabel('Frekuensi')
    plt.ylabel('Kata')
    plt.title('Top 15 Kata Paling Sering Muncul di Judul Berita')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    plt.savefig(save_path)
    print(f"Grafik frekuensi kata disimpan di: {save_path}")
    plt.close()