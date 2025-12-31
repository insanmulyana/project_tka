import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. KONFIGURASI ---
# GANTI LINK INI DENGAN LINK GOOGLE SHEETS ANDA
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Vr8LdlC2COe-zqPKFyrtqMvGFUF3XbjhaOlfkGO-oz0/edit?usp=sharing"
LOGO_FILE = "logo_sekolah.png"

st.set_page_config(page_title="Verifikasi Data TKA", layout="centered")

# --- 2. STYLE TOMBOL (BIRU NEON) ---
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #00d4ff; color: white; border-radius: 8px;
        width: 100%; font-weight: bold; height: 3.5rem; font-size: 18px;
    }
    div.stButton > button:first-child:hover { background-color: #008fb3; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KONEKSI DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def muat_data_bersih():
    st.cache_data.clear()
    df = conn.read(spreadsheet=SHEET_URL)
    # Normalisasi kolom agar tidak error jika ada spasi di Google Sheets
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df['nis'] = df['nis'].astype(str).str.strip()
    df['tgl_lahir'] = df['tgl_lahir'].astype(str).str.strip()
    return df

# --- 4. HEADER ---
col_logo, col_judul = st.columns([1, 5])
with col_logo:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=85)
with col_judul:
    st.markdown("## Verifikasi Data Siswa\n#### Sertifikat Nilai TKA")

st.divider()

# --- 5. LOGIN (SIDEBAR) ---
with st.sidebar:
    st.header("Login Siswa")
    input_nis = st.text_input("Masukkan NIS").strip()
    input_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)").strip()

# --- 6. AREA VERIFIKASI ---
if input_nis and input_tgl:
    df_siswa = muat_data_bersih()
    # Cari siswa berdasarkan NIS dan Tgl Lahir
    siswa = df_siswa[(df_siswa['nis'] == input_nis) & (df_siswa['tgl_lahir'] == input_tgl)]

    if not siswa.empty:
        idx = siswa.index[0]
        st.success(f"Data ditemukan: {siswa.at[idx, 'nama']}")
        
        # Fungsi pembantu ambil nilai kolom
        def val(k): 
            return str(siswa.at[idx, k]) if k in siswa.columns and pd.notna(siswa.at[idx, k]) else ""

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nama Lengkap", value=val('nama'), disabled=True)
            st.text_input("Tempat Lahir", value=val('tempat_lahir'), disabled=True)
            st.text_input("Nama Ayah", value=val('nama_ayah'), disabled=True)
        with col2:
            st.text_input("Kelas", value=val('kelas'), disabled=True)
            st.text_input("Tanggal Lahir", value=val('tgl_lahir'), disabled=True)
        
        status_skrg = val('status')
        st.write(f"Status Saat Ini: **{status_skrg if status_skrg else 'Belum Verifikasi'}**")

        with st.expander("Klik jika ada kesalahan data"):
            st.write("Tuliskan detail perbaikan jika ada data yang salah:")
            perbaikan_val = st.text_area("Detail Perbaikan:", value=val('catatan_perbaikan'))
        
        if st.button("SIMPAN KONFIRMASI"):
            # Tarik data terbaru tepat sebelum simpan agar tidak menimpa siswa lain
            df_final = muat_data_bersih()
            # Cari ulang baris siswa di data terbaru
            idx_final = df_final[df_final['nis'] == input_nis].index[0]
            
            if perbaikan_val.strip():
                df_final.at[idx_final, 'status'] = 'Perlu Perbaikan'
                df_final.at[idx_final, 'catatan_perbaikan'] = perbaikan_val
            else:
                df_final.at[idx_final, 'status'] = 'Data Sudah Benar'
                df_final.at[idx_final, 'catatan_perbaikan'] = ""
            
            df_final.at[idx_final, 'waktu_akses'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # SIMPAN KE GOOGLE SHEETS
            conn.update(spreadsheet=SHEET_URL, data=df_final)
            st.balloons()
            st.success("Berhasil! Data Anda sudah diperbarui di sistem pusat.")
    else:
        st.error("Data tidak ditemukan. Pastikan NIS benar dan format tanggal YYYY-MM-DD.")

# --- 7. ADMIN ---
st.write("")
with st.expander("Panel Admin"):
    pw = st.text_input("Password", type="password")
    if pw == "admin123":
        st.write("### Rekapitulasi Verifikasi")
        st.dataframe(muat_data_bersih())
