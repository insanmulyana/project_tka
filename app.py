import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# GANTI LINK INI
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Vr8LdlC2COe-zqPKFyrtqMvGFUF3XbjhaOlfkGO-oz0/edit?usp=sharing"

st.set_page_config(page_title="Verifikasi TKA", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

def muat_data_bersih():
    st.cache_data.clear()
    # Membaca data tanpa anggapan format (sebagai string semua)
    df = conn.read(spreadsheet=SHEET_URL, dtype=str) 
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    # Bersihkan spasi liar di semua sel
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

st.title("Verifikasi Data Siswa")

with st.sidebar:
    st.header("Login Siswa")
    input_nis = st.text_input("Masukkan NIS").strip()
    input_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)").strip()

if input_nis and input_tgl:
    df_siswa = muat_data_bersih()
    
    # Pencarian yang sangat longgar (case-insensitive & string-based)
    siswa = df_siswa[
        (df_siswa['nis'].astype(str) == str(input_nis)) & 
        (df_siswa['tgl_lahir'].astype(str) == str(input_tgl))
    ]

    if not siswa.empty:
        idx = siswa.index[0]
        st.success(f"Data ditemukan: {siswa.at[idx, 'nama']}")
        
        # --- TAMPILAN DATA ---
        def val(k): return str(siswa.at[idx, k]) if k in siswa.columns and pd.notna(siswa.at[idx, k]) else ""
        
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nama", value=val('nama'), disabled=True)
            st.text_input("Tempat Lahir", value=val('tempat_lahir'), disabled=True)
            st.text_input("Nama Ayah", value=val('nama_ayah'), disabled=True)
        with c2:
            st.text_input("Kelas", value=val('kelas'), disabled=True)
            st.text_input("Tgl Lahir", value=val('tgl_lahir'), disabled=True)
            
        perbaikan = st.text_area("Detail Perbaikan (Kosongkan jika benar):", value=val('catatan_perbaikan'))
        
        if st.button("SIMPAN KONFIRMASI"):
            df_final = muat_data_bersih()
            idx_f = df_final[df_final['nis'].astype(str) == str(input_nis)].index[0]
            
            df_final.at[idx_f, 'status'] = 'Perlu Perbaikan' if perbaikan.strip() else 'Data Sudah Benar'
            df_final.at[idx_f, 'catatan_perbaikan'] = perbaikan
            df_final.at[idx_f, 'waktu_akses'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn.update(spreadsheet=SHEET_URL, data=df_final)
            st.success("Tersimpan!")
            st.balloons()
    else:
        st.error("Data tidak ditemukan.")
        # --- FITUR DEBUG (HANYA MUNCUL JIKA GAGAL) ---
        with st.expander("Bantuan Admin: Cek Format Data di Sistem"):
            st.write("Format yang Anda ketik:")
            st.write(f"NIS: `{input_nis}` | Tgl: `{input_tgl}`")
            st.write("3 Data teratas di Google Sheets (perhatikan formatnya):")
            st.table(df_siswa[['nis', 'nama', 'tgl_lahir']].head(3))
