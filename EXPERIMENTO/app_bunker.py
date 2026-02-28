import streamlit as st
import requests
import json

# Configuración de la página
st.set_page_config(page_title="RADnet Búnker Móvil", page_icon="📡")

st.title("📡 RADnet: Telemetría de Campo")
st.write("---")

# Formulario de Entrada de Datos
with st.form("formulario_bunker"):
    st.subheader("📋 Registro de Inspección")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nodo = st.selectbox("Nodo", ["TH", "TBL_CENTRO", "SUR_01", "BUNKER_CENTRAL"])
        temp = st.number_input("Temperatura (°C)", value=25.0, step=0.1)
        pwr = st.number_input("Energía (V)", value=13.2, step=0.1)
        cpu = st.slider("Uso CPU (%)", 0, 100, 15)
        
    with col2:
        inspector = st.text_input("Inspector", value="Luis Alberto")
        inspec_completada = st.checkbox("¿Inspección Completada?", value=False)
        capacidad = st.number_input("Capacidad (Mbps)", value=100)
        soleos = st.number_input("Sóleos realizados", value=500) # ¡Tu telemetría personal!

    st.write("📍 **Geolocalización (Simulada)**")
    lat = st.number_input("Latitud", value=10.4806)
    lon = st.number_input("Longitud", value=-66.9036)

    # Botón de envío
    boton_disparo = st.form_submit_button("🚀 DISPARAR AL BÚNKER")

if boton_disparo:
    # 1. Empaquetamos todo en el JSON (la carga útil)
    # Importante: Usamos los nombres que tu Apps Script espera
    paquete = {
        "nodo": nodo,
        "temp": temp,
        "inspec": inspec_completada,
        "tec": f"{inspector} (Sóleos: {soleos})",
        "pwr": pwr,
        "mbps": capacidad,
        "cpu": cpu,
        "lat": lat,
        "lon": lon
    }

    # 2. La URL de tu nuevo EXEC
    url_exec = "https://script.google.com/macros/s/AKfycbwrjrnN1OH4xQ1NVE0gBxRNBJYPaqyzKVZmeGW8fpKMb8z9NhAtBzXB5ZJKwtGQfQuQ/exec"

    # 3. Disparo de artillería
    try:
        with st.spinner("Conectando con el Búnker..."):
            res = requests.post(url_exec, data=json.dumps(paquete))
            
        if "LOGRADO" in res.text:
            st.success(f"✅ ¡Victoria! El Búnker respondió: {res.text}")
            st.balloons() # ¡Un poco de celebración para esos sóleos!
        else:
            st.warning(f"⚠️ El Búnker recibió algo, pero dice: {res.text}")
            
    except Exception as e:
        st.error(f"❌ Error en la transmisión: {e}")

st.write("---")
st.caption("Arquitectura RADnet v2.0 - Seguridad y Control")
