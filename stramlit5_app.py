import streamlit as st

# --------------------------------------
# Configuración de la página
# --------------------------------------
st.set_page_config(page_title="Gráfico de emisiones CO₂", layout="wide")
st.title("📊 Gráfico de barras – Emisiones de CO₂ por país")
# --------------------------------------
# Cargar datos
# --------------------------------------
csv_path = "/Users/jaimesandoval/Desktop/grupo21/co2/emissions_per_country/annual-co2-emissions-per-country.csv"
