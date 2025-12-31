import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI ---
# GANTI LINK DI BAWAH INI DENGAN LINK GOOGLE SHEETS ANDA
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Vr8LdlC2COe-zqPKFyrtqMvGFUF3XbjhaOlfkGO-oz0/edit?usp=sharing"

st.set_page_config(page_title="Verifikasi Data TKA", layout="centered")

# CSS Tombol Tetap Sama
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #00d4ff; color: white; border-radius: 8px;
        width: 100%; font-weight: bold; height: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNGSI DATA GOOGLE SHEETS ---
def muat_data():
    # Mengubah link share menjadi link download CSV agar bisa dibaca Pandas
    csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip().str.lower()
    df['nis'] = df['nis'].astype(str)
    df['tgl_lahir'] = df['tgl_lahir'].astype(str)
    return df

# Karena update ke Google Sheets via link publik butuh library tambahan atau API,
# Untuk cara tercepat "darurat" ini, kita gunakan gsheets-connection
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)

def update_data(df_baru):
    conn.update(spreadsheet=SHEET_URL, data=df_baru)

# Load Data
df_siswa = muat_data()

# --- 3. HEADER & LOGIN (Sama Seperti Kemarin) ---
st.title("Verifikasi Data Siswa")
with st.sidebar:
    st.header("Login")
    input_nis = st.text_input("NIS")
    input_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)")

if input_nis and input_tgl:
    siswa = df_siswa[(df_siswa['nis'] == input_nis) & (df_siswa['tgl_lahir'] == input_tgl)]
    if not siswa.empty:
        idx = siswa.index[0]
        st.success(f"Halo, {siswa.at[idx, 'nama']}")
        
        # Tampilkan Data
        st.write(f"Status Saat Ini: **{siswa.at[idx, 'status']}**")
        catatan = st.text_area("Catatan Perbaikan (Kosongkan jika benar):", value=str(siswa.at[idx, 'catatan_perbaikan']) if pd.notna(siswa.at[idx, 'catatan_perbaikan']) else "")
        
        if st.button("SIMPAN KONFIRMASI"):
            # Update DataFrame
            df_siswa.at[idx, 'status'] = "Perlu Perbaikan" if catatan.strip() else "Data Sudah Benar"
            df_siswa.at[idx, 'catatan_perbaikan'] = catatan
            df_siswa.at[idx, 'waktu_akses'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # SIMPAN PERMANEN KE GOOGLE SHEETS
            update_data(df_siswa)
            st.balloons()
            st.success("DATA BERHASIL DISIMPAN PERMANEN DI GOOGLE SHEETS!")
    else:
        st.error("Data tidak cocok.")

# Admin Panel (Sama)
with st.expander("Admin"):
    if st.text_input("Password", type="password") == "admin123":
        st.dataframe(df_siswa)
