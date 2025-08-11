import streamlit as st
import pandas as pd
import joblib

# --- Load model & encoder ---
model = joblib.load("model.pkl")
scaler_y = joblib.load("scaler_y.pkl")
le_vessel = joblib.load("le_vessel.pkl")
le_rute = joblib.load("le_rute.pkl")

# --- Load data rute tiap kapal ---
df_rute = pd.read_excel("data rute tiap kapal.xlsx")

fitur = [
    'VESSEL_ENC', 'RUTE_ENC', 'Durations_per_rute_(hours)',
    'Total_Load_A/E_(kWH)', 'GENSET_LOAD',
    'DURATION_AT_PORT_(HOURS)', 'AE_PARAREL_DURATION',
    'MANEUVERING_TIME_(HOURS)', 'Durasi_Labuh_(hours)',
    'CRANE_DURATION', 'TOTAL_CRANE_OPERATED',
    'REEFER_20', 'REEFER_40', 'Shore_Connection'
]

st.title("Prediksi Konsumsi A/E HSD Kapal 🚢")

# Pilih kapal
vessel = st.selectbox("VESSEL", sorted(df_rute["VESSEL"].unique()))

# Filter rute sesuai kapal
available_routes = df_rute[df_rute["VESSEL"] == vessel]["Rute"].unique()
rute = st.selectbox("RUTE", sorted(available_routes))

# Input fitur lain
duration_route = st.number_input("Durations per rute (hours)", value=0)
total_load = st.number_input("Total Load A/E (kWH)", value=0)
genset_load = st.number_input("GENSET LOAD", value=0)
duration_port = st.number_input("Duration at port (hours)", value=0)
ae_parallel = st.number_input("AE Pararel Duration", value=0)
maneuver_time = st.number_input("Maneuvering Time (hours)", value=0)
durasi_labuh = st.number_input("Durasi Labuh (hours)", value=0)
crane_duration = st.number_input("Crane Duration", value=0)
total_crane = st.number_input("Total Crane Operated", value=0)
reefer_20 = st.number_input("Reefer 20", value=0)
reefer_40 = st.number_input("Reefer 40", value=0)
shore_conn = st.selectbox("Shore Connection", [0, 1])

if st.button("Prediksi"):
    # Encode
    vessel_enc = le_vessel.transform([vessel])[0]
    rute_enc = le_rute.transform([rute])[0]

    input_data = {
        'VESSEL_ENC': vessel_enc,
        'RUTE_ENC': rute_enc,
        'Durations_per_rute_(hours)': duration_route,
        'Total_Load_A/E_(kWH)': total_load,
        'GENSET_LOAD': genset_load,
        'DURATION_AT_PORT_(HOURS)': duration_port,
        'AE_PARAREL_DURATION': ae_parallel,
        'MANEUVERING_TIME_(HOURS)': maneuver_time,
        'Durasi_Labuh_(hours)': durasi_labuh,
        'CRANE_DURATION': crane_duration,
        'TOTAL_CRANE_OPERATED': total_crane,
        'REEFER_20': reefer_20,
        'REEFER_40': reefer_40,
        'Shore_Connection': shore_conn
    }

    X_new = pd.DataFrame([input_data])[fitur]

    y_pred_scaled = model.predict(X_new)
    y_pred_real = scaler_y.inverse_transform(
        y_pred_scaled.reshape(-1, 1)
    ).ravel()[0]

    st.success(f"Prediksi konsumsi MFO (real): {y_pred_real:,.2f} Liter")
