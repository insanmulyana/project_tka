import streamlit as st
import pandas as pd
import os
from datetime import datetime

#konfig
FILE_DATA = "data_siswa.xlsx"
LOGO_FILE = "logo_sekolah.png"

st.set_page_config(
    page_title="Verifikasi Data TKA",
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "📝",
    layout="centered"
)
# --- STYLE TOMBOL CUSTOM ---
st.markdown("""
    <style>
    /* Mengubah gaya tombol Simpan Konfirmasi */
    div.stButton > button:first-child {
        background-color: #28a745; /* Biru Neon Soft */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: 0.3s;
        width: 100%; /* Agar tombol lebar dan mudah ditekan di tablet */
    }
    div.stButton > button:first-child:hover {
        background-color: #008fb3; /* Warna saat disentuh/hover */
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

#fungsi_data
def muat_data():
    if os.path.exists(FILE_DATA):
        df = pd.read_excel(FILE_DATA)
        df.columns = df.columns.str.strip().str.lower()
        # Inisialisasi kolom jika belum ada
        for col in ['status', 'catatan_perbaikan', 'waktu_akses']:
            if col not in df.columns:
                df[col] = ""
        df['nis'] = df['nis'].astype(str)
        df['tgl_lahir'] = df['tgl_lahir'].astype(str)
        return df
    else:
        st.error(f"File {FILE_DATA} tidak ditemukan!")
        return None

def simpan_data(df):
    df.to_excel(FILE_DATA, index=False)

if 'df_siswa' not in st.session_state:
    st.session_state.df_siswa = muat_data()

#logo
col_logo, col_judul = st.columns([1, 5])
with col_logo:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=85)
with col_judul:
    st.markdown("""
        <div style='line-height: 1.2;'>
            <h3 style='margin-bottom: 0;'>VERIFIKASI DATA SISWA TKA 2025</h3>
            <p style='font-size: 18px; margin-top: 0;'>SMA KARTIKA XIX-1 BANDUNG</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

#login_siswa
with st.sidebar:
    st.header("Login Siswa")
    input_nis = st.text_input("Masukkan NIS")
    input_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)", placeholder="Contoh: 2008-05-10")

#verifikasi
if input_nis and input_tgl:
    df = st.session_state.df_siswa
    siswa = df[(df['nis'] == input_nis) & (df['tgl_lahir'] == input_tgl)]

    if not siswa.empty:
        idx = siswa.index[0]
        st.success(f"Data ditemukan: {siswa.at[idx, 'nama']}")
        
        # Grid Data Siswa
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nama Lengkap", value=siswa.at[idx, 'nama'], disabled=True)
            st.text_input("Tempat Lahir", value=siswa.at[idx, 'tempat_lahir'], disabled=True)
            st.text_input("Nama Ayah", value=siswa.at[idx, 'nama_ayah'], disabled=True)
        with col2:
            st.text_input("Kelas", value=siswa.at[idx, 'kelas'], disabled=True)
            st.text_input("Tanggal Lahir", value=siswa.at[idx, 'tgl_lahir'], disabled=True)
        
        # Status & Waktu Akses
        waktu_info = f" | Diakses pada: {siswa.at[idx, 'waktu_akses']}" if pd.notna(siswa.at[idx, 'waktu_akses']) and siswa.at[idx, 'waktu_akses'] != "" else ""
        st.write(f"Kelas: **{siswa.at[idx, 'kelas']}** | Status: **{siswa.at[idx, 'status']}**{waktu_info}")

        # Expander Perbaikan
        with st.expander("Klik di sini jika ada kesalahan data"):
            st.write("Silakan tuliskan detail perbaikan (Nama/TTL/Ayah/Kelas):")
            perbaikan_val = st.text_area("Detail Perbaikan:", 
                                         value=str(siswa.at[idx, 'catatan_perbaikan']) if pd.notna(siswa.at[idx, 'catatan_perbaikan']) else "")
        
        if st.button("Simpan Konfirmasi"):
            waktu_skrg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if perbaikan_val.strip():
                st.session_state.df_siswa.at[idx, 'status'] = 'Perlu Perbaikan'
                st.session_state.df_siswa.at[idx, 'catatan_perbaikan'] = perbaikan_val
            else:
                st.session_state.df_siswa.at[idx, 'status'] = 'Data Sudah Benar'
                st.session_state.df_siswa.at[idx, 'catatan_perbaikan'] = ""
            
            st.session_state.df_siswa.at[idx, 'waktu_akses'] = waktu_skrg
            simpan_data(st.session_state.df_siswa)
            st.success(f"Berhasil disimpan pada {waktu_skrg}. Anda bisa menutup halaman ini.")
            
    else:
        st.error("NIS atau Tanggal Lahir salah.")

#paneladmin
st.write("")
with st.expander("Panel Admin (hanya diakses admin sekolah)"):
    pw = st.text_input("Password", type="password")
    if pw == "admin123":
        st.write("### Rekapitulasi Verifikasi")
        st.dataframe(st.session_state.df_siswa)
        
        col_admin1, col_admin2 = st.columns(2)
        with col_admin1:
            csv = st.session_state.df_siswa.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data (CSV)", csv, "hasil_verifikasi.csv", "text/csv")


