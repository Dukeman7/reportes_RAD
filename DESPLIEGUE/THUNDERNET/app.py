import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------------------------------
# ⚙️ CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------
st.set_page_config(page_title="Thundernet - Despliegue", layout="wide")
st.title("⚡ EVOLUCIÓN DE DESPLIEGUE MENSUAL Y ACUMULADO")

# ----------------------------------------------------
# 💾 CARGA Y PREPARACIÓN DE DATOS (Modo Gumersinda)
# ----------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv('MAESTRO_THUNDERNET_HISTORICO.csv')
    
    # Truco de ingeniero: Diccionario para ordenar cronológicamente los 14 meses
    orden_meses = {
        'DIC-24': 1, 'ENE-25': 2, 'FEB-25': 3, 'MAR-25': 4, 'ABR-25': 5,
        'MAY-25': 6, 'JUN-25': 7, 'JUL-25': 8, 'AGO-25': 9, 'SEP-25': 10,
        'OCT-25': 11, 'NOV-25': 12, 'DIC-25': 13, 'ENE-26': 14
    }
    df['ORDEN'] = df['PERIODO'].map(orden_meses)
    df = df.sort_values('ORDEN')
    return df

df = cargar_datos()

# ----------------------------------------------------
# 🎛️ BARRA LATERAL (Filtros)
# ----------------------------------------------------
st.sidebar.header("Filtros de Búsqueda")

# Filtro 1: Estado
lista_estados = df['ESTADO'].unique().tolist()
estado_sel = st.sidebar.selectbox("Seleccione el Estado:", ["Todos"] + lista_estados)

# Filtro 2: Municipio (Dependiente del Estado)
if estado_sel == "Todos":
    lista_municipios = df['MUNICIPIO'].unique().tolist()
else:
    lista_municipios = df[df['ESTADO'] == estado_sel]['MUNICIPIO'].unique().tolist()

municipio_sel = st.sidebar.selectbox("Seleccione el Municipio:", ["Todos"] + lista_municipios)

# Aplicar filtros a la data
df_filtrado = df.copy()
if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['ESTADO'] == estado_sel]
if municipio_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['MUNICIPIO'] == municipio_sel]

# Agrupar por periodo por si se selecciona "Todos"
df_grafico = df_filtrado.groupby(['ORDEN', 'PERIODO'])[['TRANSPORTE', 'UM', 'ABONADOS']].sum().reset_index()

# Data Acumulada para la Pestaña 2
df_acumulado = df_grafico.copy()
df_acumulado['TRANSPORTE_ACUM'] = df_acumulado['TRANSPORTE'].cumsum()
df_acumulado['UM_ACUM'] = df_acumulado['UM'].cumsum()
df_acumulado['ABONADOS_ACUM'] = df_acumulado['ABONADOS'].cumsum()

# ----------------------------------------------------
# 📊 PESTAÑAS DEL DASHBOARD
# ----------------------------------------------------
tab1, tab2 = st.tabs(["📈 Evolución Mensual", "🚀 Despliegue Acumulado"])

# --- PESTAÑA 1: EVOLUCIÓN MENSUAL ---
with tab1:
    st.subheader(f"Despliegue Mensual: {estado_sel} - {municipio_sel}")
    
    # Crear gráfico de doble eje
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Línea: Transporte (Eje Izquierdo)
    fig1.add_trace(go.Scatter(x=df_grafico['PERIODO'], y=df_grafico['TRANSPORTE'],
                              mode='lines+markers', name='Transporte (Km)',
                              line=dict(width=3, color='#1f77b4')), secondary_y=False)
    
    # Línea: Última Milla (Eje Izquierdo)
    fig1.add_trace(go.Scatter(x=df_grafico['PERIODO'], y=df_grafico['UM'],
                              mode='lines+markers', name='Última Milla (Km)',
                              line=dict(width=3, color='#ff7f0e')), secondary_y=False)
    
    # Línea: Abonados (Eje Derecho)
    fig1.add_trace(go.Scatter(x=df_grafico['PERIODO'], y=df_grafico['ABONADOS'],
                              mode='lines+markers', name='Nuevos Abonados',
                              line=dict(width=3, dash='dot', color='#2ca02c')), secondary_y=True)
    
    fig1.update_layout(height=500, hovermode="x unified")
    fig1.update_yaxes(title_text="Kilómetros de Fibra (Km)", secondary_y=False)
    fig1.update_yaxes(title_text="Cantidad de Abonados", secondary_y=True)
    
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("### 📋 Tabla de Registros Mensuales")
    # Mostrar tabla limpia sin la columna auxiliar 'ORDEN'
    st.dataframe(df_filtrado.drop(columns=['ORDEN'], errors='ignore'), use_container_width=True)

# --- PESTAÑA 2: VALORES ACUMULADOS ---
with tab2:
    st.subheader(f"Crecimiento Histórico Acumulado: {estado_sel} - {municipio_sel}")
    
    # Crear gráfico de doble eje para acumulados
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig2.add_trace(go.Scatter(x=df_acumulado['PERIODO'], y=df_acumulado['TRANSPORTE_ACUM'],
                              mode='lines+markers', name='Transporte Acum. (Km)', fill='tozeroy'), secondary_y=False)
    
    fig2.add_trace(go.Scatter(x=df_acumulado['PERIODO'], y=df_acumulado['UM_ACUM'],
                              mode='lines+markers', name='Última Milla Acum. (Km)', fill='tonexty'), secondary_y=False)
    
    fig2.add_trace(go.Scatter(x=df_acumulado['PERIODO'], y=df_acumulado['ABONADOS_ACUM'],
                              mode='lines+markers', name='Abonados Totales',
                              line=dict(width=4, color='green')), secondary_y=True)
    
    fig2.update_layout(height=500, hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("### 📋 Tabla de Valores Acumulados")
    # Preparamos la tabla para mostrar
    tabla_exportar_acum = df_acumulado[['PERIODO', 'TRANSPORTE_ACUM', 'UM_ACUM', 'ABONADOS_ACUM']].copy()
    tabla_exportar_acum.columns = ['Periodo', 'Transporte Total (Km)', 'Última Milla Total (Km)', 'Abonados Totales']
    st.dataframe(tabla_exportar_acum, use_container_width=True)
