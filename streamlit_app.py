import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Mapa CO₂ por país",
    layout="wide"
)

st.title("🌍 Mapa interactivo de emisiones de CO₂ por país")
st.write("Selecciona un año para visualizar las emisiones globales.")

# -----------------------------
# Cargar datos
# -----------------------------
@st.cache_data
def load_data():
    shp_path = '/Users/jaimesandoval/Desktop/Grupo_2/co2/50m_cultural/ne_50m_admin_0_countries.shp'
    world = gpd.read_file(shp_path)
    world = world.rename(columns={'ISO_A3': 'code'})
    world['code'] = world['code'].str.upper()

    df = pd.read_csv('/Users/jaimesandoval/Desktop/Grupo_2/co2/emissions_per_country/annual-co2-emissions-per-country.csv')
    df = df.rename(columns={'Entity': 'country', 'Code': 'code', 'Year': 'year'})
    df['code'] = df['code'].str.upper()
    df = df[df['code'].str.len() == 3]

    # columna de emisiones
    value_col = [c for c in df.columns if c not in ['country', 'code', 'year']]
    df = df.rename(columns={value_col[0]: 'co2'})

    # maestro geográfico
    world_master = (
        world[['code', 'NAME', 'geometry']]
        .drop_duplicates(subset=['code'])
        .rename(columns={'NAME': 'country'})
        .set_index('code')
    )

    # preparar geojson
    geojson_world = world_master['geometry'].__geo_interface__

    return world_master, geojson_world, df

world_master, geojson_world, df = load_data()

# -----------------------------
# Función para el mapa
# -----------------------------
def make_co2_map(df_co2, year):
    co2_year = (
        df_co2[df_co2['year'] == year][['code', 'co2']]
        .groupby('code', as_index=False)
        .agg({'co2': 'sum'})
        .set_index('code')
    )

    world_y = world_master.join(co2_year, how='left')
    g_with = world_y[world_y['co2'].notna()].reset_index()
    g_no = world_y[world_y['co2'].isna()].reset_index()

    # Países con datos
    fig = px.choropleth(
        g_with,
        geojson=geojson_world,
        locations='code',
        color='co2',
        hover_name='country',
        projection='natural earth',
        color_continuous_scale='Reds'
    )

    # Países sin datos → gris
    fig_grey = px.choropleth(
        g_no,
        geojson=geojson_world,
        locations='code',
        color_discrete_sequence=['#d0d0d0'],
        hover_name='country',
        projection='natural earth'
    )

    for trace in fig_grey.data:
        trace.showlegend = False
        fig.add_trace(trace)

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        title_text=f'CO₂ emissions by country in {year}',
        title_x=0.5,
        height=650,
        margin={"r":0, "t":40, "l":0, "b":0}
    )

    return fig

# -----------------------------
# Sidebar: selección de año
# -----------------------------
years = sorted(df["year"].unique())
selected_year = st.sidebar.slider("Selecciona un año", min_value=min(years), max_value=max(years), value=1950)

# -----------------------------
# Mostrar mapa
# -----------------------------
fig = make_co2_map(df, selected_year)
st.plotly_chart(fig, use_container_width=True)
