import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI ---
# GANTI LINK DI BAWAH INI DENGAN LINK GOOGLE SHEETS ANDA (PASTIKAN SUDAH JADI EDITOR)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Vr8LdlC2COe-zqPKFyrtqMvGFUF3XbjhaOlfkGO-oz0/edit?usp=sharing"
LOGO_FILE = "logo_sekolah.png"

st.set_page_config(page_title="Verifikasi Data TKA", layout="centered")

# --- 2. STYLE TOMBOL (WARNA BIRU NEON) ---
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #00d4ff; color: white; border-radius: 8px;
        width: 100%; font-weight: bold; height: 3.5rem; font-size: 18px;
    }
    div.stButton > button:first-child:hover { background-color: #008fb3; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def muat_data_bersih():
    # Force clear cache agar selalu ambil data terbaru dari Sheets
    st.cache_data.clear()
    df = conn.read(spreadsheet=SHEET_URL)
    # Normalisasi Kolom: hapus spasi, kecilkan huruf, ganti spasi jadi underscore
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    # Pastikan NIS dan Tgl Lahir jadi String agar tidak error saat login
    df['nis'] = df['nis'].astype(str).str.strip()
    df['tgl_lahir'] = df['tgl_lahir'].astype(str).str.strip()
    return df

def update_ke_sheets(df_update):
    conn.update(spreadsheet=SHEET_URL, data=df_update)
    st.cache_data.clear()

# --- 4. HEADER ---
col_logo, col_judul = st.columns([1, 5])
with col_logo:
    import os
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=85)
with col_judul:
    st.markdown("## Verifikasi Data Siswa\n#### Sertifikat Nilai TKA")

st.divider()

# --- 5. LOGIN ---
with st.sidebar:
    st.header("Login Siswa")
    input_nis = st.text_input("Masukkan NIS").strip()
    input_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)").strip()

# --- 6. AREA VERIFIKASI ---
if input_nis and input_tgl:
    df_siswa = muat_data_bersih()
    # Cari siswa
    siswa = df_siswa[(df_siswa['nis'] == input_nis) & (df_siswa['tgl_lahir'] == input_tgl)]

    if not siswa.empty:
        idx = siswa.index[0]
        st.success(f"Data ditemukan: {siswa.at[idx, 'nama']}")
        
        # Fungsi ambil nilai agar tidak error jika kolom gak ada
        def val(k): return str(siswa.at[idx, k]) if k in siswa.columns and pd.notna(siswa.at[idx, k]) else ""

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nama Lengkap", value=val('nama'), disabled=True)
            st.text_input("Tempat Lahir", value=val('tempat_lahir'), disabled=True)
            st.text_input("Nama Ayah", value=val('nama_ayah'), disabled=True)
        with col2:
            st.text_input("Kelas", value=val('kelas'), disabled=True)
            st.text_input("Tanggal Lahir", value=val('tgl_lahir'), disabled=True)
        
        st.write(f"Status: **{val('status') if val('status') else 'Belum Verifikasi'}**")

        with st.expander("Klik jika ada kesalahan data"):
            catatan = st.text_area("Detail Perbaikan:", value=val('catatan_perbaikan'))
        
        if st.button("SIMPAN KONFIRMASI"):
            # AMBIL DATA TERBARU LAGI (PENTING AGAR TIDAK MENIMPA ORANG LAIN)
            df_final = muat_data_bersih()
            # Cari ulang index-nya di data yang paling baru
            idx_final = df_final[df_final['nis'] == input_nis].index[0]
            
            if catatan.strip():
                df_final.at[idx_final, 'status'] = 'Perlu Perbaikan'
                df_final.at[idx_final, 'catatan_perbaikan'] = catatan
            else:
                df_final.at[idx_final, 'status'] = 'Data Sudah Benar'
                df_final.at[idx_final, 'catatan_perbaikan'] = ""
            
            df_final.at[idx_final, 'waktu_akses'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # KIRIM PERMANEN
            update_ke_sheets(df_final)
            st.balloons()
            st.success("Berhasil Simpan! Data Anda sudah masuk ke sistem pusat.")
    else:
        st.error("Data tidak ditemukan. Cek NIS dan format Tanggal Lahir (YYYY-MM-DD).")

# --- 7. ADMIN ---
with st.expander("Panel Admin"):
    if st.text_input("Password", type="password") == "admin123":
        st.dataframe(muat_data_bersih())
