# Analisis Sentimen: Narasi Media vs Opini Publik Terkait Timnas Indonesia Menuju Piala Dunia 2026

## 📜 Ringkasan Proyek

Proyek ini bertujuan untuk menganalisis dan membandingkan narasi seputar **Timnas Indonesia** dalam kualifikasi Piala Dunia 2026 dari dua sudut pandang yang berbeda: **media berita profesional** dan **opini publik**.

- **Media Berita:** Diwakili oleh artikel dari portal berita online terkemuka Indonesia, yaitu **Detik.com** dan **Kompas.com**. Sumber ini cenderung menyajikan informasi faktual dan objektif.
- **Opini Publik:** Diwakili oleh komentar dari video-video relevan di **YouTube**. Sumber ini kaya akan sentimen emosional, baik dukungan (pro) maupun kritik (kontra).
<img width="1831" height="939" alt="image" src="https://github.com/user-attachments/assets/9e878d67-eab1-4b21-a8d5-8cecc6979bda" />


Dengan membandingkan kedua sumber ini, kita dapat memperoleh wawasan mendalam tentang bagaimana media membentuk narasi dan bagaimana publik meresponsnya, serta topik-topik apa yang menjadi fokus utama di masing-masing ranah.

## 🚀 Teknologi yang Digunakan

Proyek ini dibangun menggunakan serangkaian teknologi dan library Python yang modern untuk menangani setiap tahapan pipeline data.

- **Bahasa Pemrograman:** Python 3.11+
- **Manajemen Lingkungan:** `venv`
- **Pengumpulan Data (Crawling):**
    - **Portal Berita:** `httpx` & `asyncio` untuk crawling paralel yang cepat, `BeautifulSoup4` untuk parsing HTML.
    - **YouTube:** `google-api-python-client` untuk berinteraksi dengan YouTube Data API v3 secara stabil dan resmi.
- **Preprocessing & Pembersihan Data:** `pandas` untuk manipulasi data, `Sastrawi` untuk _stopword removal_ Bahasa Indonesia.
- **Analisis Sentimen:** `transformers` dari Hugging Face untuk menjalankan model Machine Learning canggih.
    - **Model:** `w11wo/indonesian-roberta-base-sentiment-classifier`, sebuah model RoBERTa yang di-_fine-tune_ untuk analisis sentimen Bahasa Indonesia dengan output rating bintang (1-5 stars).
- **Visualisasi & Dashboard:** `Streamlit` sebagai framework aplikasi web, `Plotly Express` untuk membuat grafik interaktif (hover, zoom, filter), dan `Matplotlib` + `wordcloud` untuk generasi Word Cloud.
- **Manajemen Kredensial:** `python-dotenv` untuk mengelola API Key secara aman.

## ⚙️ Arsitektur & Alur Kerja Pipeline

**1. Stasiun Pengumpulan Data (Crawling)**
   - **`src/main.py` (untuk Berita):** Menjalankan crawler `detik_crawler.py` dan `kompas_crawler.py` secara paralel untuk mengumpulkan artikel berita.
   - **`crawl_youtube.py` (untuk Opini Publik):** Menggunakan YouTube Data API v3 untuk mencari video relevan berdasarkan daftar kata kunci, kemudian mengambil ribuan komentar dari video-video tersebut.
   - **Output:** File-file `.csv` mentah di folder `data/raw/`. Proses ini bersifat inkremental (menambahkan data baru tanpa menghapus yang lama).

**2. Stasiun Pembersihan (Preprocessing)**
   - **`run_preprocessing.py`:** Script ini membaca *semua* file CSV dari `data/raw/`, menggabungkannya, menghapus duplikat, membersihkan teks (menghapus URL, mention, tanda baca), dan menstandarisasi format tanggal.
   - **Output:** Satu file master `data/processed/master_cleaned_data.csv`.

**3. Stasiun Analisis (Machine Learning)**
   - **`run_analysis.py`:** Membaca data bersih dari stasiun sebelumnya. Script ini "pintar": ia hanya akan menganalisis baris data yang belum memiliki label sentimen.
   - **Proses:** Teks bersih dikirim ke model IndoBERT (`w11wo/indonesian-roberta-base-sentiment-classifier`) untuk mendapatkan rating sentimen (1-5 stars).
   - **Output:** File final `data/final/analysis_results.csv` yang diperkaya dengan data sentimen dan siap untuk divisualisasikan.

**4. Stasiun Visualisasi (Dashboard)**
   - **`dashboard/app.py`:** Aplikasi Streamlit yang membaca file `analysis_results.csv`.
   - **Proses:** Mengubah rating bintang menjadi label (Positif, Netral, Negatif), kemudian membuat semua visualisasi secara dinamis dan interaktif menggunakan Plotly.
   - **Output:** Sebuah dashboard web interaktif yang dapat diakses melalui browser.

## 🔧 Detail Teknis & "Kunci" yang Digunakan

Untuk memastikan crawler dapat beradaptasi dengan struktur website, "kunci" (selector CSS) spesifik digunakan untuk setiap sumber.

### Detik.com
- **Daftar Artikel:** `article.list-content__item`
- **Judul:** `h3.media__title`
- **Tanggal:** `div.media__date`
- **Teks Lengkap:** `div.detail__body-text` -> `p`

### Kompas.com
- **Daftar Artikel:** `div.articleItem`
- **Judul:** `h2.articleTitle`
- **Tanggal:** `div.articlePost-date`
- **Teks Lengkap:** `div.read__content` (dengan pembersihan elemen iklan/video internal)

### YouTube (via API)
- **Pencarian Video:** `YT.search().list()`
- **Komentar:** `YT.commentThreads().list()`

## 📊 Cara Menjalankan Proyek

1.  **Clone Repository:**
    ```bash
    git clone [URL_REPOSITORY_ANDA]
    cd [NAMA_FOLDER_PROYEK]
    ```

2.  **Setup Lingkungan:**
    - Buat dan aktifkan virtual environment:
      ```bash
      python -m venv venv
      # Windows
      venv\Scripts\activate
      # macOS/Linux
      source venv/bin/activate
      ```
    - Install semua dependensi:
      ```bash
      pip install -r requirements.txt
      ```

3.  **Konfigurasi Kredensial:**
    - Buat file bernama `.env` di folder utama.
    - Isi file tersebut dengan API Key YouTube Anda:
      ```
      YT_API_KEY="AIzaSyXXXXXXXXXXXXXXXX"
      ```

4.  **Jalankan Pipeline (Bertahap):**
    - **(Wajib) Kumpulkan data YouTube:**
      ```bash
      python crawl_youtube.py
      ```
    - **(Opsional) Tambah data berita:**
      ```bash
      python src/main.py
      ```
    - **Proses semua data yang terkumpul:**
      ```bash
      python run_preprocessing.py
      ```
    - **Jalankan analisis Machine Learning:**
      ```bash
      python run_analysis.py
      ```

5.  **Tampilkan Dashboard:**
    ```bash
    streamlit run dashboard/app.py
    ```
    Buka URL yang ditampilkan di terminal pada browser Anda.

## 💡 Hasil & Kesimpulan Awal

Berdasarkan analisis data yang telah terkumpul, beberapa temuan awal yang menarik adalah:
- **Narasi Media Cenderung Netral:** Sebagian besar artikel berita memiliki sentimen netral (rating 3 bintang), yang mengindikasikan peliputan yang objektif dan fokus pada fakta pertandingan, skor, dan jadwal.
- **Opini Publik Sangat Tervokalisasi:** Komentar di YouTube menunjukkan distribusi sentimen yang jauh lebih "berwarna", dengan persentase sentimen Positif (dukungan, pujian) dan Negatif (kritik, kekecewaan) yang signifikan.
- **Fokus Topik yang Berbeda:** Analisis Word Cloud menunjukkan bahwa media lebih fokus pada kata-kata kunci terkait **taktik, nama pemain, dan event** (misal: "kualifikasi", "pertandingan", "formasi"). Sebaliknya, publik lebih sering menggunakan kata-kata yang bersifat **emosional dan evaluatif** (misal: "semangat", "mantap", "sayang", "ganti").
- **Puncak Interaksi:** Grafik tren menunjukkan lonjakan volume komentar YouTube yang signifikan di sekitar tanggal-tanggal pertandingan penting, sementara volume pemberitaan media cenderung lebih stabil.

Proyek ini berhasil membuktikan bahwa dengan menggabungkan data dari sumber media dan opini publik, kita dapat memperoleh pemahaman yang lebih holistik dan mendalam tentang sebuah isu.
