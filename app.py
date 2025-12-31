import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# GANTI LINK INI DENGAN LINK GOOGLE SHEETS ANDA
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Vr8LdlC2COe-zqPKFyrtqMvGFUF3XbjhaOlfkGO-oz0/edit?usp=sharing"

st.set_page_config(page_title="Verifikasi TKA", layout="centered")

# Koneksi menggunakan Secrets yang tadi diisi
conn = st.connection("gsheets", type=GSheetsConnection)

def muat_data():
    st.cache_data.clear()
    df = conn.read(spreadsheet=SHEET_URL)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df['nis'] = df['nis'].astype(str).str.strip()
    df['tgl_lahir'] = df['tgl_lahir'].astype(str).str.strip()
    return df

# Header & Login tetap sama
# ... (bagian header dan login)

if input_nis and input_tgl:
    df_siswa = muat_data()
    siswa = df_siswa[(df_siswa['nis'] == input_nis) & (df_siswa['tgl_lahir'] == input_tgl)]

    if not siswa.empty:
        idx = siswa.index[0]
        # (Tampilan data siswa seperti sebelumnya)
        
        if st.button("SIMPAN KONFIRMASI"):
            # Tarik data terbaru tepat sebelum simpan
            df_final = muat_data()
            idx_final = df_final[df_final['nis'] == input_nis].index[0]
            
            # Update data
            df_final.at[idx_final, 'status'] = "Data Sudah Benar" # Contoh
            df_final.at[idx_final, 'waktu_akses'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # SEKARANG PASTI BISA UPDATE
            conn.update(spreadsheet=SHEET_URL, data=df_final)
            st.success("Tersimpan Permanen!")
            st.balloons()
