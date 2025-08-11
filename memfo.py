import streamlit as st
import pandas as pd
import openpyxl

# Konfigurasi halaman dan tema
st.set_page_config(page_title="Estimasi Konsumsi MFO", page_icon="🚢🛢️", layout="centered")

# Header dengan logo dan judul
col1, col2 = st.columns([1, 9])
with col1:
    st.image("Logospil.png", width=100)  # Ganti sesuai file logo Anda
with col2:
    st.markdown("""
        <h1 style='color:#0b9d45; font-size: 36px; margin-bottom: 0;'>Estimasi Konsumsi M/E MFO</h1>
        <p style='font-size:18px; color:gray;'>Simulasi estimasi konsumsi bahan bakar berdasarkan kecepatan dan jalur pelayaran</p>
    """, unsafe_allow_html=True)

# Data loading dengan cache
@st.cache_data
def load_baseline():
    return pd.read_excel('9 Juni Data Baseline semua kapal.xlsx')

@st.cache_data
def load_distance_data():
    return pd.read_excel('Data Jarak antar rute komplit.xlsx')

baseline = load_baseline()
baseline['ME RPM (RPM)'] = baseline['ME RPM (RPM)'].astype(str) 
distance_data = load_distance_data()

# Pilihan kapal
daftar_kapal = baseline['VESSEL'].dropna().unique().tolist()
vessel = st.selectbox(f"🚢 Vessel (Total = {len(daftar_kapal)} Kapal)", ["-- Pilih Vessel --"] + sorted(daftar_kapal))

# Buat salinan untuk akses bebas
all_pols = distance_data["POL"].unique().tolist()
all_pods = distance_data["POD"].unique().tolist()

def get_filtered_options(selected_pol, selected_pod, distance_data):
    if selected_pol != "-- Pilih POL --" and selected_pod != "-- Pilih POD --":
        filtered_pod_options = distance_data[distance_data["POL"] == selected_pol]["POD"].unique().tolist()
        filtered_pol_options = distance_data[distance_data["POD"] == selected_pod]["POL"].unique().tolist()
    elif selected_pol != "-- Pilih POL --":
        filtered_pod_options = distance_data[distance_data["POL"] == selected_pol]["POD"].unique().tolist()
        filtered_pol_options = all_pols
    elif selected_pod != "-- Pilih POD --":
        filtered_pol_options = distance_data[distance_data["POD"] == selected_pod]["POL"].unique().tolist()
        filtered_pod_options = all_pods
    else:
        filtered_pol_options = all_pols
        filtered_pod_options = all_pods
    return filtered_pol_options, filtered_pod_options

# Inisialisasi session state
if "pol" not in st.session_state:
    st.session_state.pol = "-- Pilih POL --"
if "pod" not in st.session_state:
    st.session_state.pod = "-- Pilih POD --"

filtered_pol_options, filtered_pod_options = get_filtered_options(
    st.session_state.pol, st.session_state.pod, distance_data
)

pol = st.selectbox(
    "🏗️ Port of Loading (POL)",
    ["-- Pilih POL --"] + sorted(filtered_pol_options),
    index=(["-- Pilih POL --"] + sorted(filtered_pol_options)).index(st.session_state.pol)
    if st.session_state.pol in sorted(filtered_pol_options) or st.session_state.pol == "-- Pilih POL --"
    else 0,
    key="pol"
)

pod = st.selectbox(
    "🏗️ Port of Discharge (POD)",
    ["-- Pilih POD --"] + sorted(filtered_pod_options),
    index=(["-- Pilih POD --"] + sorted(filtered_pod_options)).index(st.session_state.pod)
    if st.session_state.pod in sorted(filtered_pod_options) or st.session_state.pod == "-- Pilih POD --"
    else 0,
    key="pod"
)

# Slider RPM berdasarkan kapal
def rpm_slider(kapal):
    if kapal == "-- Pilih Vessel --":
        return None
    
    rpm_list = baseline[baseline['VESSEL'] == kapal]['ME RPM (RPM)'].dropna().unique().tolist()
    rpm_list = [str(rpm) for rpm in rpm_list]
    rpm_list = sorted(rpm_list)

    if len(rpm_list) == 0:
        st.warning("⚠️ Tidak ada data RPM untuk kapal ini.")
        return None
    elif len(rpm_list) == 1:
        st.markdown(f"🔧 RPM: {rpm_list[0]}")
        return rpm_list[0]
    else:
        return st.selectbox("🔧 Pilih RPM", options=rpm_list)


rpm = rpm_slider(vessel) if vessel != "-- Pilih Vessel --" else None

# Input kecepatan kapal
speed = st.number_input("⚙️ Masukkan Kecepatan Kapal (KNOT)", min_value=0.1, value=10.0)

# Fungsi estimasi
@st.cache_data
def estimate_mfo_and_duration(vessel, pol, pod, rpm, speed):
    route = distance_data[(distance_data['POL'] == pol) & (distance_data['POD'] == pod)]
    if route.empty:
        return None, None, "🛑 Rute tidak ditemukan dalam data jarak."

    dist_nmile = route.iloc[0]['NMILE']
    duration_exp = dist_nmile / speed

    mfo_row = baseline[(baseline['VESSEL'] == vessel) & (baseline['ME RPM (RPM)'] == rpm)]
    if mfo_row.empty:
        return None, None, "🛑 Data baseline tidak tersedia untuk kombinasi kapal dan RPM ini."

    mfoperjam = mfo_row.iloc[0]['mean M/E MFO per Jam']
    mfo_exp = duration_exp * mfoperjam

    return duration_exp, mfo_exp, None

# Tombol prediksi
if st.button("📊 Hitung Estimasi",type="primary"):
    if vessel != "Choose" and pol and pod and rpm is not None:
        duration, mfo, error = estimate_mfo_and_duration(vessel, pol, pod, rpm, speed)
        if error:
            st.warning(error)
        else:
            st.success("✅ Estimasi berhasil dihitung.")
            st.markdown(f"""
                ### 🔍 Hasil Estimasi Perjalanan

                - **Durasi Perjalanan (perkiraan):** `{duration:.2f}` jam  
                - **Konsumsi M/E MFO (perkiraan):** `{mfo:,.2f}` liter
            """)
    else:
        st.warning("⚠️ Mohon lengkapi semua input terlebih dahulu sebelum menghitung.")
