import streamlit as st
import requests
import json

st.set_page_config(page_title="RADnet Búnker Móvil", page_icon="📡")

st.title("📡 RADnet: Telemetría de Campo")
st.write("---")

# Formulario Limpio
with st.form("formulario_bunker"):
    st.subheader("📋 Registro de Inspección")
    
    col1, col2 = st.columns(2)
    with col1:
        nodo = st.selectbox("Nodo", ["TH", "TBL_CENTRO", "SUR_01", "BUNKER_CENTRAL"])
        temp = st.number_input("Temperatura (°C)", value=25.0)
        pwr = st.number_input("Energía (V)", value=13.2)
        
    with col2:
        inspector = st.text_input("Inspector", value="Luis Alberto")
        inspec_completada = st.checkbox("¿Inspección Completada?", value=False)
        soleos = st.number_input("Sóleos realizados", value=770)

    boton_disparo = st.form_submit_button("🚀 DISPARAR AL BÚNKER")

if boton_disparo:
    paquete = {
        "nodo": nodo,
        "tec": f"{inspector} (Sóleos: {soleos})",
        "temp": temp,
        "pwr": pwr,
        "inspec": inspec_completada,
        "mbps": 100,
        "cpu": 15,
        "lat": 10.48,
        "lon": -66.90
    }

    url_exec = "https://script.google.com/macros/s/AKfycbwrjrnN1OH4xQ1NVE0gBxRNBJYPaqyzKVZmeGW8fpKMb8z9NhAtBzXB5ZJKwtGQfQuQ/exec"

    try:
        res = requests.post(url_exec, data=json.dumps(paquete))
        if "LOGRADO" in res.text:
            st.success(f"✅ ¡Victoria! {res.text}")
            st.balloons()
        else:
            st.warning(f"Respuesta: {res.text}")
    except Exception as e:
        st.error(f"Error: {e}")
