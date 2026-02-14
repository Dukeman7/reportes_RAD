import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="RADnet Monitoring", layout="wide")
st.title("📡 RADnet Telecom: Auditoría de Red")

# Área para pegar el reporte
report_input = st.text_area("Pegue aquí el reporte de texto (Mañana o Tarde):", height=200)

def parse_data(text):
    if not text: return None
    data = {}
    # Extracción de CPUs
    cpus = re.findall(r"CPU ([\w-]+):\s*(\d+)%", text)
    cpu_dict = {f"CPU {name}": int(val) for name, val in cpus}
    
    # Extracción de Nodos (Convirtiendo todo a Mbps para comparar)
    nodes = re.findall(r"-NODO\s*([\w-]+)\s*:.*?\n(?:PROMEDIO|Promedio):\s*([\d.]+)\s*(\w+)", text, re.IGNORECASE | re.DOTALL)
    node_dict = {}
    for name, val, unit in nodes:
        v = float(val)
        if unit.lower() == 'gbps': v *= 1000
        node_dict[name] = v
        
    return cpu_dict, node_dict

if report_input:
    cpus, nodes = parse_data(report_input)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Carga de Procesadores")
        df_cpu = pd.DataFrame(list(cpus.items()), columns=['Equipo', 'Carga %'])
        fig_cpu = px.bar(df_cpu, x='Equipo', y='Carga %', color='Carga %', 
                         color_continuous_scale='RdYlGn_r', range_y=[0,100])
        st.plotly_chart(fig_cpu, use_container_width=True)

    with col2:
        st.subheader("🌐 Tráfico por Nodo (Mbps)")
        df_nodes = pd.DataFrame(list(nodes.items()), columns=['Nodo', 'Mbps'])
        fig_nodes = px.pie(df_nodes, values='Mbps', names='Nodo', hole=.3)
        st.plotly_chart(fig_nodes, use_container_width=True)

    st.success("✅ Datos extraídos correctamente. Listo para auditar.")
