import streamlit as st
import pandas as pd
import plotly.express as px
import re
import numpy as np

st.set_page_config(page_title="RADnet Monitoring v4.4", layout="wide")
st.title("📡 RADnet Telecom: Auditoría de Red (Escala v4.1)")

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
    
    # --- 1. LÓGICA DE COLORES v4.1 (Brillantes y Sólidos) ---
    def asignar_color(valor):
        if valor < 20: return 'lime'      # <--- Brillo Intenso (Óptimo)
        if valor < 40: return 'limegreen' # Óptimo/Bajo
        if valor < 60: return 'yellow'    # Medio (Atención)
        if valor < 80: return 'orange'    # Alto
        return 'red'                      # Crítico

    df_cpu['Color'] = df_cpu['Carga %'].apply(asignar_color)
    
    # --- 2. CÁLCULO DE EJE Y (Múltiplo de 5) ---
    max_real = df_cpu['Carga %'].max() if not df_cpu.empty else 10
    objetivo_y = max_real * 1.20 # Máxima carga + 20%
    limite_y = int(np.ceil(objetivo_y / 5) * 5) # Redondeo al múltiplo de 5 superior
    if limite_y < 10: limite_y = 10 # Mínimo visual

    st.subheader(f"📊 Carga de Procesadores (Perspectiva ajustada a {limite_y}%)")
    
    col_chart, col_tatuaje = st.columns([4, 1]) # 4 partes gráfico, 1 parte tatuaje

    with col_chart:
        # Gráfico v4.1 con escala discreta y rango Y calculado
        fig_cpu = px.bar(df_cpu, x='Equipo', y='Carga %', 
                         color='Color',
                         color_discrete_map={'lime': '#00FF00', 'limegreen': '#32CD32', 'yellow': '#FFFF00', 'orange': '#FFA500', 'red': '#FF0000'},
                         range_y=[0, limite_y],
                         text_auto=True)
        fig_cpu.update_layout(showlegend=False)
        st.plotly_chart(fig_cpu, use_container_width=True)

    with col_tatuaje:
        # --- 3. EL "TATUAJE" (Imagen Fija y Brillante) ---
        st.write("**Escala de Referencia RADnet**")
        # Simulamos la imagen usando Markdown y CSS para que sea "brillante"
        st.markdown("""
        <div style="border: 2px solid white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; color: black;">
          <div style="background-color: #FF0000; padding: 5px; border-radius: 3px; margin-bottom: 2px;">80-100% Crítico</div>
          <div style="background-color: #FFA500; padding: 5px; border-radius: 3px; margin-bottom: 2px;">60-80% Alto</div>
          <div style="background-color: #FFFF00; padding: 5px; border-radius: 3px; margin-bottom: 2px;">40-60% Medio</div>
          <div style="background-color: #32CD32; padding: 5px; border-radius: 3px; margin-bottom: 2px;">20-40% Óptimo-Bajo</div>
          <div style="background-color: #00FF00; padding: 5px; border-radius: 3px; margin-bottom: 2px;">00-20% Óptimo</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Esta escala es fija y sirve como guía visual.")

    # --- 🍕 TRÁFICO POR NODOS (DOBLE PIE) ---
    st.divider()
    df_nodes = pd.DataFrame(list(nodes.items()), columns=['Nodo', 'Mbps'])
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Total (con TH)**")
        st.plotly_chart(px.pie(df_nodes, values='Mbps', names='Nodo', hole=.4), use_container_width=True)
    with c2:
        st.write("**Secundarios (Sin TH)**")
        df_sub = df_nodes[df_nodes['Nodo'] != 'TH']
        st.plotly_chart(px.pie(df_sub, values='Mbps', names='Nodo', hole=.4), use_container_width=True)
