# dashboard/app.py (Versi Professional Enhanced)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Analisis Sentimen: Timnas di Mata Media & Publik",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS UNTUK STYLING PROFESIONAL ---
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .insight-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .insight-box h4 {
        color: #1b5e20;
        margin-bottom: 0.5rem;
    }
    .insight-box p {
        color: #2e7d32;
        font-size: 1rem;
        line-height: 1.6;
    }
    .stTab {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI-FUNGSI BANTUAN & VISUALISASI ---

@st.cache_data
def load_data(path):
    """Memuat dan memproses data awal."""
    try:
        df = pd.read_csv(path)
        star_to_sentiment = {
            '1 star': 'Negatif', '2 stars': 'Negatif',
            '3 stars': 'Netral',
            '4 stars': 'Positif', '5 stars': 'Positif'
        }
        df.loc[:, 'sentiment_label'] = df['sentiment'].map(star_to_sentiment).fillna('Netral')
        df['formatted_date'] = pd.to_datetime(df['formatted_date'])
        
        def categorize_source(row):
            if row['source_type'] == 'youtube':
                return 'Opini Publik (YouTube)'
            else:
                return 'Media Berita'
        df['source_category'] = df.apply(categorize_source, axis=1)
        return df
    except FileNotFoundError:
        return None

def create_sentiment_donut_chart(df):
    """Membuat donut chart untuk distribusi sentimen keseluruhan."""
    sentiment_counts = df['sentiment_label'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.5,
        marker=dict(colors=['#2ca02c', '#d62728', '#7f7f7f']),
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title='<b>Distribusi Sentimen Keseluruhan</b>',
        annotations=[dict(text='Sentimen<br>Umum', x=0.5, y=0.5, font_size=16, showarrow=False)],
        showlegend=True,
        height=400
    )
    return fig

def create_sentiment_comparison_bar(df):
    """Membuat bar chart perbandingan sentimen antara Berita dan YouTube."""
    comparison_data = df.groupby('source_category')['sentiment_label'].value_counts(normalize=True).mul(100).rename('percentage').reset_index()
    
    fig = px.bar(
        comparison_data,
        x='source_category',
        y='percentage',
        color='sentiment_label',
        barmode='group',
        title='<b>Perbandingan Proporsi Sentimen: Media Berita vs Opini Publik</b>',
        labels={'percentage': 'Persentase (%)', 'source_category': 'Tipe Sumber', 'sentiment_label': 'Sentimen'},
        color_discrete_map={'Positif': '#2ca02c', 'Negatif': '#d62728', 'Netral': '#7f7f7f'},
        template='plotly_white',
        text=comparison_data['percentage'].apply(lambda x: f'{x:.1f}%')
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis_title="Persentase Komentar/Artikel", 
        xaxis_title=None,
        height=450
    )
    return fig

def create_trend_line_chart(df):
    """Membuat line chart tren per hari, dipisahkan berdasarkan kategori sumber."""
    trend_data = df.set_index('formatted_date').groupby('source_category').resample('D').size().reset_index(name='count')
    
    fig = px.line(
        trend_data,
        x='formatted_date',
        y='count',
        color='source_category',
        title='<b>Tren Volume Pemberitaan vs Opini Publik per Hari</b>',
        labels={'formatted_date': 'Tanggal', 'count': 'Jumlah Konten', 'source_category': 'Kategori Sumber'},
        template='plotly_white',
        markers=True
    )
    fig.update_layout(
        xaxis_title=None, 
        yaxis_title="Jumlah Artikel/Komentar",
        height=450,
        hovermode='x unified'
    )
    return fig

def create_sentiment_timeline(df):
    """Membuat timeline sentimen dari waktu ke waktu."""
    daily_sentiment = df.set_index('formatted_date').groupby(['source_category', pd.Grouper(freq='D')])['sentiment_label'].apply(
        lambda x: (x == 'Positif').sum() - (x == 'Negatif').sum()
    ).reset_index(name='sentiment_score')
    
    fig = px.line(
        daily_sentiment,
        x='formatted_date',
        y='sentiment_score',
        color='source_category',
        title='<b>Skor Sentimen dari Waktu ke Waktu (Positif - Negatif)</b>',
        labels={'formatted_date': 'Tanggal', 'sentiment_score': 'Skor Sentimen', 'source_category': 'Kategori'},
        template='plotly_white'
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Netral")
    fig.update_layout(height=400)
    return fig

def create_top_keywords_chart(df, source_type, top_n=15):
    """Membuat bar chart untuk kata kunci teratas."""
    if 'cleaned_full_text' not in df.columns or df['cleaned_full_text'].dropna().empty:
        return None
    
    stopwords_tambahan = {'yg', 'gak', 'piala', 'dunia', 'vs', 'detik', 'com', 
                          'juga', 'akan', 'namun', 'baca', 'kata', 'tim', 'nya', 'skuad',
                          'yang', 'ini', 'itu', 'dari', 'untuk', 'pada', 'adalah', 'dengan'}
    
    full_text = ' '.join(df['cleaned_full_text'].dropna()).lower().split()
    filtered_words = [word for word in full_text if word not in stopwords_tambahan and len(word) > 3]
    word_freq = Counter(filtered_words).most_common(top_n)
    
    if not word_freq:
        return None
    
    keywords_df = pd.DataFrame(word_freq, columns=['Kata Kunci', 'Frekuensi'])
    
    fig = px.bar(
        keywords_df,
        x='Frekuensi',
        y='Kata Kunci',
        orientation='h',
        title=f'<b>Top {top_n} Kata Kunci: {source_type}</b>',
        template='plotly_white',
        color='Frekuensi',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        showlegend=False
    )
    return fig

def create_word_cloud(df, title):
    """Membuat visualisasi Word Cloud."""
    if 'cleaned_full_text' not in df.columns or df['cleaned_full_text'].dropna().empty:
        return None
    
    full_text = ' '.join(df['cleaned_full_text'].dropna())
    stopwords_tambahan = ['timnas', 'indonesia', 'piala', 'dunia', 'vs', 'detik', 'com', 
                          'juga', 'akan', 'namun', 'baca', 'kata', 'tim', 'garuda', 'skuad', 'yg', 'gak', 'nya', 'ga', 'sama', 'aja']
    
    wordcloud = WordCloud(
        width=800, height=400, background_color='white',
        colormap='viridis', stopwords=stopwords_tambahan,
        max_words=100, relative_scaling=0.5
    ).generate(full_text)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
    return fig

def get_data_collection_info():
    """Informasi tentang metode pengumpulan data."""
    return {
        'Periode Crawling': 'Oktober 2024 - Januari 2025',
        'Sumber Data Berita': ['Detik.com', 'Kompas.com'],
        'Sumber Data Publik': 'Komentar YouTube (Video resmi PSSI dan highlight pertandingan)',
        'Total Data Terkumpul': '20,000+ entri',
        'Metode Analisis Sentimen': 'nlptown/bert-base-multilingual-uncased-sentiment',
        'Kata Kunci Crawling': ['timnas indonesia', 'kualifikasi piala dunia', 'garuda asia', 'pssi']
    }

# --- UI UTAMA DASHBOARD ---

# Header Banner
st.markdown("""
    <div class="main-header">
        <h1>⚽ Analisis Sentimen: Timnas Indonesia di Mata Media & Publik</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Membandingkan narasi dari <b>Media Berita</b> dengan opini <b>Publik di YouTube</b> 
            terkait Kualifikasi Piala Dunia 2026
        </p>
    </div>
""", unsafe_allow_html=True)

# Load data
df = load_data('data/final/analysis_results.csv')

if df is None:
    st.error("⚠️ File 'data/final/analysis_results.csv' tidak ditemukan. Jalankan pipeline preprocessing dan analisis terlebih dahulu.")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/320px-Flag_of_Indonesia.svg.png", width=150)
        
        st.header("⚙️ Pengaturan Dashboard")
        
        # Filter Tanggal
        min_date = df['formatted_date'].min().date()
        max_date = df['formatted_date'].max().date()
        
        selected_date_range = st.date_input(
            "📅 Rentang Waktu Analisis:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        st.markdown("---")
        
        # Informasi Metodologi
        st.subheader("📊 Metodologi Penelitian")
        info = get_data_collection_info()
        
        with st.expander("🔍 Detail Pengumpulan Data"):
            st.write(f"**Periode:** {info['Periode Crawling']}")
            st.write(f"**Total Data:** {info['Total Data Terkumpul']}")
            st.write(f"**Metode Analisis:** {info['Metode Analisis Sentimen']}")
            
        with st.expander("📰 Sumber Berita"):
            for source in info['Sumber Data Berita']:
                st.write(f"• {source}")
                
        with st.expander("🔑 Kata Kunci Pencarian"):
            for keyword in info['Kata Kunci Crawling']:
                st.write(f"• `{keyword}`")

    # Terapkan filter tanggal
    start_date = pd.to_datetime(selected_date_range[0])
    end_date = pd.to_datetime(selected_date_range[1]) if len(selected_date_range) > 1 else pd.to_datetime(selected_date_range[0])
    filtered_df = df[(df['formatted_date'] >= start_date) & (df['formatted_date'] <= end_date)].copy()
    
    # --- METRICS CARDS ---
    st.markdown("## 📊 Ringkasan Eksekutif")
    
    df_media = filtered_df[filtered_df['source_category'] == 'Media Berita']
    df_publik = filtered_df[filtered_df['source_category'] == 'Opini Publik (YouTube)']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📝 Total Konten Dianalisis", 
            f"{len(filtered_df):,}",
            delta=f"{len(filtered_df)} entri",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "📰 Artikel Berita", 
            f"{len(df_media):,}",
            delta=f"{len(df_media)/len(filtered_df)*100:.1f}%",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "💬 Komentar YouTube", 
            f"{len(df_publik):,}",
            delta=f"{len(df_publik)/len(filtered_df)*100:.1f}%",
            delta_color="off"
        )
    
    with col4:
        sentiment_positive_pct = (filtered_df['sentiment_label'] == 'Positif').sum() / len(filtered_df) * 100
        st.metric(
            "😊 Sentimen Positif", 
            f"{sentiment_positive_pct:.1f}%",
            delta="Keseluruhan",
            delta_color="normal"
        )

    st.markdown("---")

    # --- TAB ANALISIS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview Sentimen", 
        "📈 Perbandingan Detail", 
        "🔑 Analisis Kata Kunci",
        "💭 Word Cloud",
        "📚 Data Mentah"
    ])
    
    with tab1:
        st.markdown("### 🎯 Gambaran Umum Sentimen")
        
        col_donut1, col_donut2 = st.columns(2)
        
        with col_donut1:
            fig_overall = create_sentiment_donut_chart(filtered_df)
            st.plotly_chart(fig_overall, use_container_width=True)
        
        with col_donut2:
            # Sentiment by source
            sentiment_by_source = filtered_df.groupby(['source_category', 'sentiment_label']).size().reset_index(name='count')
            fig_source = px.bar(
                sentiment_by_source,
                x='source_category',
                y='count',
                color='sentiment_label',
                title='<b>Distribusi Sentimen per Kategori Sumber</b>',
                color_discrete_map={'Positif': '#2ca02c', 'Negatif': '#d62728', 'Netral': '#7f7f7f'},
                barmode='stack',
                template='plotly_white'
            )
            fig_source.update_layout(height=400)
            st.plotly_chart(fig_source, use_container_width=True)
        
        # Timeline sentimen
        st.markdown("### 📅 Timeline Sentimen")
        fig_timeline = create_sentiment_timeline(filtered_df)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
    with tab2:
        st.markdown("### 🔍 Analisis Komparatif Mendalam")
        
        fig_comparison = create_sentiment_comparison_bar(filtered_df)
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        fig_trend = create_trend_line_chart(filtered_df)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Insights Otomatis
        st.markdown("### 💡 Key Insights")
        
        if not df_media.empty:
            media_sentiment_dist = df_media['sentiment_label'].value_counts(normalize=True)
            dominant_media = media_sentiment_dist.idxmax()
            pct_media = media_sentiment_dist.max() * 100
            
            st.markdown(f"""
            <div class="insight-box">
                <h4>📰 Media Berita</h4>
                <p>Sentimen dominan: <b>{dominant_media}</b> ({pct_media:.1f}%)</p>
                <p>Media cenderung objektif dan fokus pada peliputan fakta dengan narasi yang lebih terstruktur.</p>
            </div>
            """, unsafe_allow_html=True)
        
        if not df_publik.empty:
            publik_sentiment_dist = df_publik['sentiment_label'].value_counts(normalize=True)
            dominant_publik = publik_sentiment_dist.idxmax()
            pct_publik = publik_sentiment_dist.max() * 100
            is_polarized = (publik_sentiment_dist.get('Positif', 0) > 0.3) and (publik_sentiment_dist.get('Negatif', 0) > 0.3)
            
            st.markdown(f"""
            <div class="insight-box">
                <h4>💬 Opini Publik</h4>
                <p>Sentimen dominan: <b>{dominant_publik}</b> ({pct_publik:.1f}%)</p>
                <p>{'⚠️ Opini sangat terpolarisasi antara Positif dan Negatif.' if is_polarized else '✅ Respon emosional kuat dari suporter dengan sentimen yang konsisten.'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🔑 Kata Kunci Paling Sering Muncul")
        
        col_kw1, col_kw2 = st.columns(2)
        
        with col_kw1:
            fig_kw_media = create_top_keywords_chart(df_media, "Media Berita")
            if fig_kw_media:
                st.plotly_chart(fig_kw_media, use_container_width=True)
            else:
                st.info("Data tidak cukup untuk analisis kata kunci berita.")
        
        with col_kw2:
            fig_kw_publik = create_top_keywords_chart(df_publik, "Opini Publik")
            if fig_kw_publik:
                st.plotly_chart(fig_kw_publik, use_container_width=True)
            else:
                st.info("Data tidak cukup untuk analisis kata kunci publik.")
        
        st.info("📌 **Interpretasi:** Kata kunci yang muncul menunjukkan fokus diskusi. Media berita cenderung menyebutkan nama pemain, taktik, dan jadwal. Publik lebih ekspresif dengan kata-kata emosional.")
    
    with tab4:
        st.markdown("### 💭 Visualisasi Word Cloud")
        
        col_wc1, col_wc2 = st.columns(2)
        
        with col_wc1:
            fig_wc_media = create_word_cloud(df_media, "Topik Utama di Media Berita")
            if fig_wc_media:
                st.pyplot(fig_wc_media)
            else:
                st.write("⚠️ Data tidak cukup untuk word cloud berita.")
        
        with col_wc2:
            fig_wc_publik = create_word_cloud(df_publik, "Topik Utama di Komentar Publik")
            if fig_wc_publik:
                st.pyplot(fig_wc_publik)
            else:
                st.write("⚠️ Data tidak cukup untuk word cloud publik.")
    
    with tab5:
        st.markdown("### 📊 Tabel Data Lengkap")
        
        # Filter tambahan
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_sentiment = st.multiselect(
                "Filter Sentimen:",
                options=filtered_df['sentiment_label'].unique(),
                default=filtered_df['sentiment_label'].unique()
            )
        
        with col_f2:
            filter_source = st.multiselect(
                "Filter Sumber:",
                options=filtered_df['source_category'].unique(),
                default=filtered_df['source_category'].unique()
            )
        
        display_df = filtered_df[
            (filtered_df['sentiment_label'].isin(filter_sentiment)) &
            (filtered_df['source_category'].isin(filter_source))
        ]
        
        st.dataframe(
            display_df[['formatted_date', 'source_category', 'sentiment_label', 'cleaned_full_text']],
            use_container_width=True,
            height=500
        )
        
        # Download button
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name=f"analisis_sentimen_timnas_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p><b>Dashboard Analisis Sentimen Timnas Indonesia</b></p>
            <p>Data dikumpulkan melalui web scraping dan dianalisis menggunakan BERT Model</p>
            <p>© 2025 | Untuk keperluan penelitian dan presentasi</p>
        </div>
    """, unsafe_allow_html=True)