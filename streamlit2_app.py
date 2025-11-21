import streamlit as st
import pandas as pd
import plotly.express as px
# --------------------------------------
# Configuración de la página
# --------------------------------------
st.set_page_config(
    page_title="Gráfico de Barras",
    layout="wide"
)

st.title("📊 Generador de Gráfico de Barras en Streamlit")

st.write("Carga un archivo CSV y selecciona las columnas para generar el gráfico.")

# --------------------------------------
# Subir archivo CSV
# --------------------------------------
uploaded_file = st.file_uploader("Sube un archivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Vista previa del archivo:")
    st.dataframe(df.head(), use_container_width=True)

    # Selección de columnas
    st.sidebar.header("Configuración del gráfico")
    x_col = st.sidebar.selectbox("Columna para el eje X", df.columns)
    y_col = st.sidebar.selectbox("Columna para el eje Y", df.columns)

    # Generar gráfico
    fig = px.bar(df, x=x_col, y=y_col, title=f"Gráfico de barras: {y_col} por {x_col}")
    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📥 Esperando que subas un archivo CSV...")
