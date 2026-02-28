import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la App
st.set_page_config(page_title="RADnet Thunder-Vision", layout="centered")

# 2. Carga de Datos
@st.cache_data
def load_data():
    df = pd.read_csv('MEGADATA_THUNDER_DEPURADA.csv')
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    return df.sort_values('FECHA')

df = load_data()
fechas = sorted(df['FECHA'].unique())

# 3. Estado de la Sesión (Navegación)
if 'mes_idx' not in st.session_state:
    st.session_state.mes_idx = 0

# 4. Controles (Botones)
col_atras, col_mes, col_adelante = st.columns([1, 2, 1])
with col_atras:
    if st.button("⬅️ ATRÁS") and st.session_state.mes_idx > 0:
        st.session_state.mes_idx -= 1
with col_adelante:
    if st.button("ADELANTE ➡️") and st.session_state.mes_idx < len(fechas) - 1:
        st.session_state.mes_idx += 1

# Datos del Mes Seleccionado
fecha_sel = fechas[st.session_state.mes_idx]
mes_actual = df[df['FECHA'] == fecha_sel]
acumulado = df[df['FECHA'] <= fecha_sel]

total_clientes = mes_actual['ABONADOS'].sum()
troncal_mes = mes_actual['TRONCAL'].sum()
milla_mes = mes_actual['ULTIMA_MILLA'].sum()

# 5. EL CÍRCULO DINÁMICO (RADIO SEGÚN CLIENTES)
st.title(f"📊 {fecha_sel.strftime('%B %Y').upper()}")

radio = 100 + (total_clientes / 100) # Ajuste dinámico
st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-top: 50px;">
        <div style="
            width: {radio}px; height: {radio}px; 
            border-radius: 50%; background-color: #2ECC71; 
            display: flex; justify-content: center; align-items: center; 
            box-shadow: 0px 0px 20px #2ECC71; color: white;
            transition: all 0.5s ease-in-out;">
            <div style="text-align: center;">
                <span style="font-size: 14px;">ALTAS MES</span><br>
                <b style="font-size: 28px;">{int(total_clientes):,}</b>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 6. INDICADORES "GLUCOSA" (KPIs)
st.markdown("---")
st.subheader("🛠️ Despliegue de Fibra")
c1, c2 = st.columns(2)
with c1:
    st.metric("Troncal del Mes", f"{troncal_mes:.2f} km")
    st.caption(f"Acumulado: {acumulado['TRONCAL'].sum():.2f} km")
with c2:
    st.metric("Última Milla Mes", f"{milla_mes:.2f} km")
    st.caption(f"Acumulado: {acumulado['ULTIMA_MILLA'].sum():.2f} km")

# 7. GRÁFICO DE TRÁFICO (Carga la imagen generada)
st.image('grafico_trafico_2025.png', use_column_width=True)
