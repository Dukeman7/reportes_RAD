import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="RADnet Monitoring v4.1", layout="wide")
st.title("📡 RADnet Telecom: Auditoría de Red")

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
    
    # --- 🎯 AQUÍ ESTÁ LA CORRECCIÓN DEL COLOR ---
    # Creamos una columna de color basada en el valor real, no en la posición relativa
    def asignar_color(valor):
        if valor < 15: return 'lime'      # Verde lima-limón (Baja carga)
        if valor < 70: return 'green'     # Verde estándar (Operación normal)
        if valor < 85: return 'yellow'    # Amarillo (Atención)
        return 'red'                      # Rojo (Crítico)

    df_cpu['Color'] = df_cpu['Carga %'].apply(asignar_color)
    
    # Escala Y dinámica (20% sobre el máximo)
    max_val = df_cpu['Carga %'].max() if not df_cpu.empty else 10
    limite_y = max_val * 1.2

    st.subheader(f"📊 Carga de Procesadores (Escala ajustada a {limite_y:.1f}%)")
    
    # Usamos color_discrete_map para que respete nuestros colores fijos
    fig_cpu = px.bar(df_cpu, x='Equipo', y='Carga %', 
                     color='Color',
                     color_discrete_map={'lime': '#32CD32', 'green': '#008000', 'yellow': '#FFFF00', 'red': '#FF0000'},
                     range_y=[0, limite_y],
                     text_auto=True)
    
    fig_cpu.update_layout(showlegend=False) # Limpiamos la leyenda de colores
    st.plotly_chart(fig_cpu, use_container_width=True)

    # --- 🍕 TRÁFICO POR NODOS (DOBLE VISTA) ---
    st.divider()
    df_nodes = pd.DataFrame(list(nodes.items()), columns=['Nodo', 'Mbps'])
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**Vista Global (con TH)**")
        st.plotly_chart(px.pie(df_nodes, values='Mbps', names='Nodo', hole=.4), use_container_width=True)
    with c2:
        st.write("**Vista Distribución (Sin TH)**")
        df_sub = df_nodes[df_nodes['Nodo'] != 'TH']
        st.plotly_chart(px.pie(df_sub, values='Mbps', names='Nodo', hole=.4), use_container_width=True)
