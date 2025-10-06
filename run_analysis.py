#!/usr/bin/env python3
# run_analysis.py
# Versi: Optimized single-file untuk menjalankan di VSCode (CPU-safe + progress bar + resume)
# Usage: python run_analysis.py
#
# Pastikan dependensi:
# pip install pandas torch transformers tqdm

import os
import sys
import time
import math
import argparse
import pandas as pd
import torch
from transformers import pipeline
from tqdm import tqdm

# ----------------------
# Config (ubah jika perlu)
# ----------------------
CLEANED_DATA_PATH = 'data/processed/master_cleaned_data.csv'
FINAL_OUTPUT_PATH = 'data/final/analysis_results.csv'
CHECKPOINT_PATH = 'data/final/analysis_checkpoint.csv'  # file partial untuk resume
BATCH_SIZE_CPU = 4      # aman untuk laptop CPU tanpa GPU
BATCH_SIZE_GPU = 32     # jika ada GPU, bisa dinaikkan
CHECKPOINT_INTERVAL = 5 # simpan checkpoint tiap N batch (ganti kalau mau)
TRUNCATE_LENGTH = 256   # max chars to send ke model (mengurangi token)
CPU_NUM_THREADS = 2     # batasi agar laptop tidak panas berlebih

# ----------------------
# Safety / Performance env
# ----------------------
os.environ.setdefault("OMP_NUM_THREADS", str(CPU_NUM_THREADS))
os.environ.setdefault("OPENBLAS_NUM_THREADS", str(CPU_NUM_THREADS))
try:
    torch.set_num_threads(CPU_NUM_THREADS)
except Exception:
    pass

# ----------------------
# Helper functions
# ----------------------
def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def load_dataframe(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path)

def save_dataframe(df, path):
    safe_mkdir(os.path.dirname(path) or ".")
    df.to_csv(path, index=False)

def choose_model_name():
    """Pilih model adaptif: jika ada GPU, pakai Roberta sentiment (lebih kuat).
       Jika CPU-only, pakai model ringan untuk inference lebih cepat dan aman.
    """
    if torch.cuda.is_available():
        # Model Roberta sentiment yang lebih kuat (but heavier). Hanya jika GPU tersedia.
        return "w11wo/indonesian-roberta-base-sentiment-classifier"
    else:
        # Model ringan cocok untuk CPU
        return "indobenchmark/indobert-lite-base-p1"

# ----------------------
# Main process
# ----------------------
def main():
    parser = argparse.ArgumentParser(description="Run sentiment analysis (optimized for local laptop).")
    parser.add_argument("--input", "-i", default=CLEANED_DATA_PATH, help="Path to cleaned CSV input.")
    parser.add_argument("--output", "-o", default=FINAL_OUTPUT_PATH, help="Path to final output CSV.")
    parser.add_argument("--checkpoint", "-c", default=CHECKPOINT_PATH, help="Path to checkpoint CSV for resume.")
    parser.add_argument("--batch-size", "-b", type=int, default=None, help="Override batch size (auto by default).")
    parser.add_argument("--force-model", "-m", default=None, help="Force a specific HF model name.")
    args = parser.parse_args()

    input_path = args.input
    out_path = args.output
    ckpt_path = args.checkpoint

    # --- load data ---
    try:
        df = load_dataframe(input_path)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    if 'cleaned_full_text' not in df.columns:
        print("[ERROR] Kolom 'cleaned_full_text' tidak ditemukan dalam CSV. Pastikan preprocessing selesai.")
        sys.exit(1)

    # normalize columns
    df['cleaned_full_text'] = df['cleaned_full_text'].fillna('').astype(str)
    if 'sentiment' not in df.columns:
        df['sentiment'] = pd.NA
    if 'sentiment_score' not in df.columns:
        df['sentiment_score'] = pd.NA

    # ---- resume support: jika checkpoint ada, muat dan update df agar skip yang sudah diproses ----
    if os.path.exists(ckpt_path):
        try:
            df_ckpt = pd.read_csv(ckpt_path)
            # Expect same index/rows; merge sentiment back to original df by an identifier.
            # If original CSV has an 'id' column, prefer it. Otherwise rely on index alignment.
            if 'id' in df.columns and 'id' in df_ckpt.columns:
                df = df.set_index('id')
                df_ckpt = df_ckpt.set_index('id')
                df.update(df_ckpt)
                df = df.reset_index()
                print(f"[INFO] Resume: checkpoint '{ckpt_path}' loaded and merged by 'id'.")
            else:
                # fallback: assume same ordering; match by positional index only if lengths equal
                if len(df_ckpt) == len(df):
                    df.update(df_ckpt)
                    print(f"[INFO] Resume: checkpoint '{ckpt_path}' loaded and merged by position.")
                else:
                    print(f"[WARN] Checkpoint found but size mismatch (checkpoint={len(df_ckpt)} rows, input={len(df)} rows). Ignoring checkpoint.")
        except Exception as e:
            print(f"[WARN] Gagal memuat checkpoint '{ckpt_path}': {e}. Akan mulai dari awal.")

    # select rows that still need analysis
    todo_mask = df['sentiment'].isnull() | (df['sentiment'] == '') | df['sentiment'].isna()
    df_todo = df[todo_mask].copy()
    df_to_analyze = df_todo[df_todo['cleaned_full_text'].str.strip() != ''].copy()

    if df_to_analyze.empty:
        print("[INFO] Tidak ada teks baru untuk dianalisis. Menyimpan output (jika belum ada) dan keluar.")
        save_dataframe(df, out_path)
        print(f"[INFO] Hasil tersimpan di: {out_path}")
        return

    total_texts = len(df_to_analyze)
    print(f"[INFO] Ditemukan {total_texts} teks valid yang akan dianalisis.")

    # --- choose model & device ---
    model_name = args.force_model if args.force_model else choose_model_name()
    device = 0 if torch.cuda.is_available() else -1
    auto_batch = BATCH_SIZE_GPU if device == 0 else BATCH_SIZE_CPU
    batch_size = args.batch_size if args.batch_size is not None else auto_batch

    print(f"[INFO] Menggunakan model: {model_name}")
    print(f"[INFO] Device: {'GPU' if device == 0 else 'CPU'} | Batch size: {batch_size} | Truncate length: {TRUNCATE_LENGTH}")

    # --- load pipeline (with try/except agar error model download ter-handle) ---
    try:
        sentiment_classifier = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=device
        )
    except Exception as e:
        print(f"[ERROR] Gagal memuat model '{model_name}': {e}")
        print("Jika koneksi lambat atau model besar, pertimbangkan memaksa model yang lebih ringan dengan --force-model.")
        sys.exit(1)

    # prepare texts and indices (to map results back reliably)
    df_to_analyze = df_to_analyze.reset_index()  # original index in column 'index'
    original_indices = df_to_analyze['index'].tolist()
    texts = df_to_analyze['cleaned_full_text'].str[:TRUNCATE_LENGTH].tolist()

    num_batches = math.ceil(len(texts) / batch_size)
    print(f"[INFO] Total batch: {num_batches}")

    results = [None] * len(texts)  # placeholder for preserving order
    # If checkpoint existed and provided partial results, try reuse them (merging already done earlier)

    # --- batch loop with tqdm console progress ---
    try:
        for b in tqdm(range(num_batches), desc="Menganalisis Sentimen", unit="batch"):
            start = b * batch_size
            end = min(start + batch_size, len(texts))
            batch_texts = texts[start:end]
            # call model on batch
            try:
                batch_results = sentiment_classifier(batch_texts)
                # sometimes pipeline returns labels in same order => assign
                for i, res in enumerate(batch_results):
                    results[start + i] = res
            except Exception as batch_err:
                # fallback: process single-by-single for robustness
                print(f"\n[WARN] Batch {b+1} gagal ({batch_err}). Mencoba single-item fallback...")
                for i, txt in enumerate(batch_texts):
                    try:
                        single_res = sentiment_classifier(txt)
                        # pipeline returns list even for single string; normalize:
                        if isinstance(single_res, list):
                            single_res = single_res[0] if len(single_res) > 0 else {'label': 'error', 'score': 0.0}
                        results[start + i] = single_res
                    except Exception as single_err:
                        print(f"[WARN] Single text at idx {start+i} gagal: {single_err}. Mark as error.")
                        results[start + i] = {'label': 'error', 'score': 0.0}
            # checkpoint save every N batches
            if (b + 1) % CHECKPOINT_INTERVAL == 0 or (b + 1) == num_batches:
                # map results back into a small df chunk and update master df
                chunk_indices = original_indices[start:end]
                chunk_labels = [ (r.get('label','error') if isinstance(r, dict) else 'error') for r in results[start:end] ]
                chunk_scores = [ (r.get('score',0.0) if isinstance(r, dict) else 0.0) for r in results[start:end] ]
                # create small df to update
                df_chunk = pd.DataFrame({
                    'index': chunk_indices,
                    'sentiment': chunk_labels,
                    'sentiment_score': chunk_scores
                }).set_index('index')
                # update original df by index
                df = df.set_index(df.index)  # ensure index is index
                # map values (we'll use .loc for indices)
                for idx, row in df_chunk.iterrows():
                    # idx corresponds to original df index
                    try:
                        df.at[idx, 'sentiment'] = row['sentiment']
                        df.at[idx, 'sentiment_score'] = row['sentiment_score']
                    except Exception:
                        # ignore if index missing
                        pass
                # persist checkpoint to allow resume later
                # write subset of main df (only rows with non-null sentiment) to checkpoint
                try:
                    # save full df (safe) as checkpoint and final to avoid data loss
                    save_dataframe(df.reset_index(drop=False), ckpt_path)
                    save_dataframe(df.reset_index(drop=False), out_path)
                    tqdm.write(f"[INFO] Checkpoint & partial results saved at batch {b+1}.")
                except Exception as io_err:
                    tqdm.write(f"[WARN] Gagal menyimpan checkpoint: {io_err}")

    except KeyboardInterrupt:
        print("\n[WARN] Proses dihentikan manual (KeyboardInterrupt). Menyimpan checkpoint terakhir...")
        # perform saving similar to checkpoint: update df with any gathered results so far
        # map all filled results back
        for pos, res in enumerate(results):
            if res is None:
                continue
            orig_idx = original_indices[pos]
            label = res.get('label','error') if isinstance(res, dict) else 'error'
            score = res.get('score', 0.0) if isinstance(res, dict) else 0.0
            try:
                df.at[orig_idx, 'sentiment'] = label
                df.at[orig_idx, 'sentiment_score'] = score
            except Exception:
                pass
        save_dataframe(df.reset_index(drop=False), ckpt_path)
        save_dataframe(df.reset_index(drop=False), out_path)
        print(f"[INFO] Checkpoint & partial saved to '{ckpt_path}' and '{out_path}'. Keluar.")
        sys.exit(0)

    # --- end batch loop ---
    # map remaining results back to df
    for pos, res in enumerate(results):
        if res is None:
            # mark as error/unprocessed
            label = 'error'
            score = 0.0
        else:
            label = res.get('label','error') if isinstance(res, dict) else 'error'
            score = res.get('score', 0.0) if isinstance(res, dict) else 0.0
        orig_idx = original_indices[pos]
        try:
            df.at[orig_idx, 'sentiment'] = label
            df.at[orig_idx, 'sentiment_score'] = score
        except Exception:
            pass

    # final save
    save_dataframe(df.reset_index(drop=False), out_path)
    # also remove checkpoint (or keep if you prefer)
    try:
        if os.path.exists(ckpt_path):
            os.remove(ckpt_path)
    except Exception:
        pass

    print(f"[SUCCESS] Selesai. Hasil disimpan di: {out_path}")

if __name__ == "__main__":
    main()
