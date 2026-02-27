import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="RADnet Monitoring v4.0", layout="wide")
st.title("📡 RADnet Telecom: Auditoría de Red de Alto Nivel")

report_input = st.text_area("Pegue aquí el reporte de texto:", height=200)

def parse_data(text):
    if not text: return None, None
    # Extracción de CPUs
    cpus = re.findall(r"CPU ([\w-]+):\s*(\d+)%", text)
    cpu_dict = {f"CPU {name}": int(val) for name, val in cpus}
    
    # Extracción de Nodos con conversión a Mbps
    nodes = re.findall(r"-NODO\s*([\w-]+)\s*:.*?\n(?:PROMEDIO|Promedio):\s*([\d.]+)\s*(Mbps|Gbps)", text, re.IGNORECASE | re.DOTALL)
    node_dict = {}
    for name, val, unit in nodes:
        v = float(val)
        if unit.lower() == 'gbps': v *= 1000
        node_dict[name.upper()] = round(v, 2)
        
    return cpu_dict, node_dict

if report_input:
    cpus, nodes = parse_data(report_input)
    
    # --- 1. PROCESADORES (GRÁFICO DE BARRAS) ---
    st.subheader("📊 Estado de Carga de Procesadores")
    df_cpu = pd.DataFrame(list(cpus.items()), columns=['Equipo', 'Carga %'])
    
    # Cálculo de escala Y: 20% por encima del máximo valor detectado
    max_carga = df_cpu['Carga %'].max() if not df_cpu.empty else 10
    limite_y = max_carga * 1.20 if max_carga > 0 else 20

    # Escala de colores corregida: Verde hasta el 70%, Amarillo al 85%, Rojo al 90%+
    fig_cpu = px.bar(df_cpu, x='Equipo', y='Carga %', color='Carga %',
                     color_continuous_scale=[[0, 'green'], [0.7, 'green'], [0.85, 'yellow'], [1, 'red']],
                     range_y=[0, limite_y],
                     text_auto=True)
    
    fig_cpu.update_layout(coloraxis_showscale=False) # Quitamos la leyenda lateral para limpiar
    st.plotly_chart(fig_cpu, use_container_width=True)

    # --- 2. TRÁFICO POR NODOS (DOBLE PIE) ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    df_nodes = pd.DataFrame(list(nodes.items()), columns=['Nodo', 'Mbps'])
    
    with col_a:
        st.subheader("🌐 Distribución Total (Incluye TH)")
        fig_total = px.pie(df_nodes, values='Mbps', names='Nodo', hole=.4,
                           title="Participación de TH en la Red")
        st.plotly_chart(fig_total, use_container_width=True)

    with col_b:
        st.subheader("🛰️ Distribución Interna (Sin TH)")
        # Filtramos TH para ver la distribución real de los nodos menores
        df_sin_th = df_nodes[df_nodes['Nodo'] != 'TH']
        if not df_sin_th.empty:
            fig_interna = px.pie(df_sin_th, values='Mbps', names='Nodo', hole=.4,
                                title="Balance entre Nodos Secundarios",
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_interna, use_container_width=True)
        else:
            st.info("No hay otros nodos para comparar además de TH.")

    st.success(f"✅ Auditoría completada. Escala de visualización ajustada a {limite_y:.1f}% max.")
