# src/analysis/sentiment_analyzer.py

from textblob import TextBlob
# <-- INI ADALAH IMPORT YANG BENAR, MENGGUNAKAN DEEP-TRANSLATOR
from deep_translator import GoogleTranslator
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def translate_to_english(text):
    """
    Menerjemahkan teks dari Bahasa Indonesia ke Bahasa Inggris menggunakan deep-translator.
    """
    if not text.strip():
        return ""
    
    try:
        # Cara memanggilnya sedikit berbeda: GoogleTranslator(source, target).translate(text)
        translated_text = GoogleTranslator(source='id', target='en').translate(text)
        return translated_text
    except Exception as e:
        print(f"   - Error saat menerjemahkan: {e}")
        return "" # Kembalikan string kosong jika gagal

def analyze_sentiment(english_text):
    """
    Fungsi ini tidak berubah.
    Menganalisis sentimen teks berbahasa Inggris menggunakan TextBlob.
    """
    if not english_text:
        return 'netral'

    analysis = TextBlob(english_text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0:
        return 'positif'
    elif polarity < 0:
        return 'negatif'
    else:
        return 'netral'

def plot_sentiment_distribution(sentiment_counts, save_path):
    """
    Fungsi ini tidak berubah.
    Membuat pie chart dari distribusi sentimen dan menyimpannya.
    """
    labels = sentiment_counts.index
    sizes = sentiment_counts.values
    color_map = {'positif': '#66ff66', 'negatif': '#ff6666', 'netral': '#c0c0c0'}
    colors = [color_map.get(label, '#cccccc') for label in labels]
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title('Distribusi Sentimen Pemberitaan Timnas (via Deep Translator)')
    plt.axis('equal')
    
    plt.savefig(save_path)
    print(f"Grafik distribusi sentimen disimpan di: {save_path}")
    plt.close()