import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Thundernet BI - Control CONATEL", layout="wide")

# --- ESTILO GUMERSINDA ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Thundernet: Análisis de Crecimiento")
st.markdown("---")

# 1. CARGA DE DATA
@st.cache_data
def load_and_clean():
    df = pd.read_csv('data_dashboard_thunder.csv')
    # Mapeo cronológico para ordenar meses (Gumersinda Rule: Ordenar por tiempo, no por letra)
    meses_orden = {
        'ENERO':1, 'FEBRERO':2, 'MARZO':3, 'ABRIL':4, 'MAYO':5, 'JUNIO':6,
        'JULIO':7, 'AGOSTO':8, 'SEPTIEMBRE':9, 'OCTUBRE':10, 'NOVIEMBRE':11, 'DICIEMBRE':12
    }
    def get_sort_key(m):
        m = str(m).upper()
        # Buscamos el año en el nombre del archivo o mes
        import re
        ano = re.findall(r'\d{4}', m)
        ano = int(ano[0]) if ano else 2025
        num_mes = next((v for k,v in meses_orden.items() if k in m), 1)
        return ano * 100 + num_mes

    df['ORDEN'] = df['MES'].apply(get_sort_key)
    return df.sort_values('ORDEN')

df = load_and_clean()

# 2. FILTROS LATERALES
with st.sidebar:
    st.image("https://thundernet.com.ve/wp-content/uploads/2021/05/logo-thundernet.png", width=200) # Ajustar URL si es necesario
    st.header("Explorador Geográfico")
    estado_sel = st.selectbox("Seleccione Estado", options=sorted(df['ESTADO'].unique()))
    municipio_sel = st.selectbox("Seleccione Municipio", options=sorted(df[df['ESTADO']==estado_sel]['MUNICIPIO'].unique()))

# 3. FILTRADO DE DATA
df_mun = df[(df['ESTADO'] == estado_sel) & (df['MUNICIPIO'] == municipio_sel)]

# 4. CÁLCULO DE ACUMULADOS
# Pivotamos para tener columnas por TIPO
df_pivot = df_mun.pivot_table(index=['ORDEN', 'MES'], columns='TIPO', values='VALOR', aggfunc='sum').fillna(0).reset_index()

# Asegurar que existan las columnas para evitar errores si un mes no tiene un tipo
for col in ['ABONADOS', 'TRONCAL', 'MILLA']:
    if col not in df_pivot: df_pivot[col] = 0

df_pivot['ABONADOS_ACUM'] = df_pivot['ABONADOS'].cumsum()
df_pivot['FIBRA_TOTAL'] = (df_pivot['TRONCAL'] + df_pivot['MILLA']).cumsum()

# 5. DASHBOARD DE INDICADORES (KPIs)
st.subheader(f"📍 Detalle: {municipio_sel}, {estado_sel}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Abonados Mes", f"{df_pivot['ABONADOS'].iloc[-1]:,.0f}")
c2.metric("Abonados Acumulados", f"{df_pivot['ABONADOS_ACUM'].iloc[-1]:,.0f}")
c3.metric("Km Fibra Mes", f"{(df_pivot['TRONCAL'].iloc[-1] + df_pivot['MILLA'].iloc[-1]):,.2f}")
c4.metric("Fibra Total (Km)", f"{df_pivot['FIBRA_TOTAL'].iloc[-1]:,.2f}")

# 6. GRÁFICAS DE EVOLUCIÓN
st.markdown("---")
tab1, tab2 = st.tabs(["📊 Crecimiento Mensual", "📈 Totales Acumulados"])

with tab1:
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Barras de Abonados
    fig1.add_trace(go.Bar(x=df_pivot['MES'], y=df_pivot['ABONADOS'], name="Abonados (Mensual)", marker_color='#FFD700'), secondary_y=False)
    # Líneas de Fibra
    fig1.add_trace(go.Scatter(x=df_pivot['MES'], y=df_pivot['TRONCAL'], name="Troncal (Km)", line=dict(color='#00CED1')), secondary_y=True)
    fig1.add_trace(go.Scatter(x=df_pivot['MES'], y=df_pivot['MILLA'], name="Última Milla (Km)", line=dict(color='#FF00FF')), secondary_y=True)
    
    fig1.update_layout(title="Evolución de Nuevos Registros", template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    # Área Acumulada Abonados
    fig2.add_trace(go.Scatter(x=df_pivot['MES'], y=df_pivot['ABONADOS_ACUM'], name="Total Clientes", fill='tozeroy', line=dict(color='gold')), secondary_y=False)
    # Línea Fibra Total
    fig2.add_trace(go.Scatter(x=df_pivot['MES'], y=df_pivot['FIBRA_TOTAL'], name="Total Red (Km)", line=dict(color='cyan', width=4)), secondary_y=True)
    
    fig2.update_layout(title="Crecimiento Histórico (Acumulado)", template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

st.dataframe(df_pivot[['MES', 'ABONADOS', 'TRONCAL', 'MILLA', 'ABONADOS_ACUM']].style.format(precision=2))
