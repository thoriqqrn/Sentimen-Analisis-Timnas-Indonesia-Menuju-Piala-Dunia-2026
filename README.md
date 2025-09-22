# Analisis Media Timnas Indonesia Menuju Piala Dunia 2026
<img width="2560" height="1709" alt="image" src="https://github.com/user-attachments/assets/5c2d9905-2a8e-4089-a71c-e9dfa0117933" />

Proyek ini bertujuan untuk mengumpulkan dan menganalisis sentimen publik serta tren pemberitaan mengenai "Timnas Indonesia Piala Dunia 2026" dari berbagai sumber media sosial (Facebook) dan portal berita online Indonesia.

## Pipeline Proyek
1.  **Data Collection**: Crawling data dari Facebook dan portal berita.
2.  **Data Preprocessing**: Membersihkan dan menstandarisasi data teks.
3.  **Data Storage**: Menyimpan data ke format terstruktur (CSV/JSON).
4.  **Data Analysis**: Analisis frekuensi kata, sentimen, dan tren.
5.  **Data Visualization**: Membuat visualisasi dari hasil analisis.

## Cara Menjalankan Proyek
1.  Clone repository ini.
2.  Buat dan aktifkan virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # atau venv\Scripts\activate untuk Windows
    ```
3.  Install dependensi yang dibutuhkan:
    ```bash
    pip install -r requirements.txt
    ```
4.  Buat file `.env` dari `.env.example` dan isi kredensial yang diperlukan.
5.  Jalankan pipeline utama:
    ```bash
    python src/main.py
    ```
