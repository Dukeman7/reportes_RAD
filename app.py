import streamlit as st
import pandas as pd
import plotly.graph_objects as go # Usamos Graph Objects para control total
import re

st.set_page_config(page_title="RADnet Monitoring v4.3", layout="wide")
st.title("📡 RADnet Telecom: Auditoría con Escala Tatuada")

report_input = st.text_area("Pegue aquí el reporte de texto:", height=150)

def parse_data(text):
    if not text: return None, None
    cpus = re.findall(r"CPU ([\w-]+):\s*(\d+)%", text)
    cpu_dict = {f"CPU {name}": int(val) for name, val in cpus}
    nodes = re.findall(r"-NODO\s*([\w-]+)\s*:.*?\n(?:PROMEDIO|Promedio):\s*([\d.]+)\s*(Mbps|Gbps)", text, re.IGNORECASE | re.DOTALL)
    node_dict = {name.upper(): (float(val) * 1000 if unit.lower() == 'gbps' else float(val)) for name, val, unit in nodes}
    return cpu_dict, node_dict

if report_input:
    cpus, nodes = parse_data(report_input)
    df_cpu = pd.DataFrame(list(cpus.items()), columns=['Equipo', 'Carga %'])
    
    # --- 🎨 CONSTRUCCIÓN DEL GRÁFICO CON FONDO TATUADO ---
    fig = go.Figure()

    # 1. Agregamos las barras de datos (en color negro o gris oscuro para que contrasten)
    fig.add_trace(go.Bar(
        x=df_cpu['Equipo'],
        y=df_cpu['Carga %'],
        marker_color='rgb(40, 40, 40)', 
        text=df_cpu['Carga %'],
        textposition='outside',
        name='Carga Real'
    ))

    # 2. "TATUAMOS" EL FONDO (Zonas fijas de color)
    # Definimos los rectángulos de fondo (0-20, 20-40, 40-60, 60-80, 80-100)
    zonas = [
        {'y0': 0,  'y1': 20, 'color': 'rgba(0, 255, 0, 0.2)', 'label': 'Óptimo'},      # Verde
        {'y0': 20, 'y1': 40, 'color': 'rgba(173, 255, 47, 0.2)', 'label': 'Bajo'},     # Verde Lima
        {'y0': 40, 'y1': 60, 'color': 'rgba(255, 255, 0, 0.2)', 'label': 'Medio'},     # Amarillo
        {'y0': 60, 'y1': 80, 'color': 'rgba(255, 165, 0, 0.2)', 'label': 'Alto'},      # Naranja
        {'y0': 80, 'y1': 100, 'color': 'rgba(255, 0, 0, 0.2)', 'label': 'Crítico'}    # Rojo
    ]

    for zona in zonas:
        fig.add_hrect(y0=zona['y0'], y1=zona['y1'], fillcolor=zona['color'], 
                      layer="below", line_width=0, annotation_text=zona['label'], 
                      annotation_position="left")

    # Ajustes de layout
    fig.update_layout(
        yaxis=dict(range=[0, 100], title="Carga %"),
        xaxis=dict(title="Equipos CGNAT / Router"),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.subheader("📊 Monitoreo con Escala de Seguridad Permanente")
    st.plotly_chart(fig, use_container_width=True)

    # --- 🍕 SECCIÓN DE TRÁFICO (DOBLE PIE) ---
    st.divider()
    df_nodes = pd.DataFrame(list(nodes.items()), columns=['Nodo', 'Mbps'])
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Capacidad Total**")
        st.plotly_chart(px.pie(df_nodes, values='Mbps', names='Nodo', hole=.4), use_container_width=True)
    with c2:
        st.write("**Distribución Nodos Secundarios (Sin TH)**")
        df_sub = df_nodes[df_nodes['Nodo'] != 'TH']
        st.plotly_chart(px.pie(df_sub, values='Mbps', names='Nodo', hole=.4), use_container_width=True)
