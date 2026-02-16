import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="RADnet NOC v2.0", page_icon="📡")

# Estilo para que Gumersinda no se queje de la estética
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True) # <-- ESTE ES EL CAMBIO

st.title("📡 RADnet: Gestión Operativa v2.0")
st.info("Complete las secciones para generar el reporte técnico normado.")

# --- SECCIÓN 1: IDENTIFICACIÓN ---
with st.expander("📅 Ventana de Observación", expanded=True):
    col1, col2 = st.columns(2)
    fecha_hoy = col1.date_input("Fecha", datetime.now())
    rango_hora = col2.text_input("Ventana (Ej: 08:00 a 20:00)", "08:00 a 20:00")

# --- SECCIÓN 2: RENDIMIENTO (CPUs) ---
with st.expander("💻 Uso de CPU (Procesadores)"):
    c1, c2, c3 = st.columns(3)
    cpu_cgnat = c1.slider("CGNAT-CIRION (%)", 0, 100, 5)
    cpu_2216 = c2.slider("2216-CIRION (%)", 0, 100, 10)
    cpu_un = c3.slider("326-UN (%)", 0, 100, 15)
    c4, c5 = st.columns(2)
    cpu_th = c4.slider("326-TH (%)", 0, 100, 5)
    cpu_tbl = c5.slider("326-TBL (%)", 0, 100, 8)

# --- SECCIÓN 3: TRÁFICO Y NODOS ---
with st.expander("🌐 Tráfico de Red (VNET)"):
    v_max = st.number_input("Consumo Máximo VNET (Gbps)", 0.0, 7.0, 3.5)
    v_avg = st.number_input("Tráfico Promedio VNET (Gbps)", 0.0, 7.0, 2.1)
    st.write("---")
    st.subheader("Tráfico por Nodos (Mbps)")
    n1, n2, n3 = st.columns(3)
    t_tbl = n1.number_input("TBL", 0.0)
    t_3esq = n2.number_input("3ESQ", 0.0)
    t_th = n3.number_input("TH", 0.0)
    n4, n5 = st.columns(2)
    t_dbc = n4.number_input("DBC", 0.0)
    t_suda = n5.number_input("SUDA (Antiguo SUDAME)", 0.0)

# --- SECCIÓN 4: ESTADO ELÉCTRICO ---
with st.expander("⚡ Monitor Eléctrico (Sede UN)"):
    v_volt = st.number_input("Voltaje RMS Promedio (V)", 100.0, 130.0, 120.0)
    est_electrico = st.select_slider("Nivel de Alerta", options=["VERDE", "AMARILLA", "NARANJA", "ROJA"])
    obs = st.text_area("Observaciones", "Comportamiento usual del sistema.")

# --- GENERADOR DE PDF ---
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE OPERATIVO RADNET", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=f"Fecha: {fecha_hoy} | Ventana: {rango_hora}", ln=True, align='C')
    pdf.ln(10)
    
    # Tabla de CPUs
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, "ESTADO DE PROCESADORES (CPU)", ln=True, fill=True)
    pdf.cell(0, 10, f"CGNAT: {cpu_cgnat}% | 2216: {cpu_2216}% | UN: {cpu_un}% | TH: {cpu_th}% | TBL: {cpu_tbl}%", ln=True)
    
    pdf.ln(5)
    pdf.cell(0, 10, "TRÁFICO VNET Y NODOS", ln=True, fill=True)
    pdf.cell(0, 10, f"Max: {v_max} Gbps | Prom: {v_avg} Gbps", ln=True)
    pdf.cell(0, 10, f"Nodos (Mbps) -> TBL: {t_tbl} | 3ESQ: {t_3esq} | TH: {t_th} | SUDA: {t_suda}", ln=True)
    
    pdf.ln(5)
    pdf.cell(0, 10, "MONITOR ELÉCTRICO (UN)", ln=True, fill=True)
    pdf.cell(0, 10, f"Voltaje: {v_volt}V | Alerta: {est_electrico}", ln=True)
    pdf.multi_cell(0, 10, f"Observaciones: {obs}")
    
    return pdf.output(dest='S').encode('latin-1')

if st.button("🚀 PROCESAR Y GENERAR PDF"):
    pdf_data = generar_pdf()
    st.success("✅ Reporte procesado correctamente.")
    st.download_button(label="📥 Descargar Reporte PDF", data=pdf_data, file_name=f"Reporte_RAD_{fecha_hoy}.pdf", mime="application/pdf")
