import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Emisiones de CO₂ por país",
    layout="wide"
)

st.title("🌍 Emisiones de CO₂ por país")
st.write("Mapa interactivo + gráfico de barras a partir de tus datos de emisiones.")

# -----------------------------
# Cargar datos (con caché)
# -----------------------------
@st.cache_data
def load_data():
    # 👇 Ajusta estas rutas a tu carpeta si cambian
    shp_path = '/Users/jaimesandoval/Desktop/Grupo_2/co2/50m_cultural/ne_50m_admin_0_countries.shp'
    csv_path = '/Users/jaimesandoval/Desktop/Grupo_2/co2/emissions_per_country/annual-co2-emissions-per-country.csv'

    # cargar shapefile natural earth
    world = gpd.read_file(shp_path)
    # estandarizar columna iso3
    world = world.rename(columns={'ISO_A3': 'code'})
    world['code'] = world['code'].str.upper()

    # cargar emisiones
    df = pd.read_csv(csv_path)
    df = df.rename(columns={'Entity': 'country', 'Code': 'code', 'Year': 'year'})
    df['code'] = df['code'].str.upper()

    # filtrar a códigos iso válidos
    df = df[df['code'].str.len() == 3]

    # quedarnos con la columna de emisiones
    value_col = [c for c in df.columns if c not in ['country', 'code', 'year']]
    df = df.rename(columns={value_col[0]: 'co2'})

    # maestro de países: una sola fila por code, como base para todos los años
    world_master = (
        world[['code', 'NAME', 'geometry']]
        .drop_duplicates(subset=['code'])
        .rename(columns={'NAME': 'country'})
        .set_index('code')
    )

    # geojson fijo indexado por code (iso3)
    geojson_world = world_master['geometry'].__geo_interface__

    return world_master, geojson_world, df

world_master, geojson_world, df = load_data()

# -----------------------------
# Función para el mapa
# -----------------------------
def make_co2_map(df_co2, year):
    # emisiones del año seleccionado, agregadas por país
    co2_year = (
        df_co2[df_co2['year'] == year][['code', 'co2']]
        .groupby('code', as_index=False)
        .agg({'co2': 'sum'})
        .set_index('code')
    )

    # unir al maestro: aquí nunca se pierden países
    world_y = world_master.join(co2_year, how='left')

    # países con dato vs sin dato
    g_with = world_y[world_y['co2'].notna()].reset_index()
    g_no = world_y[world_y['co2'].isna()].reset_index()

    # capa 1: países con dato → escala continua
    fig = px.choropleth(
        g_with,
        geojson=geojson_world,
        locations='code',            # usa el iso3
        color='co2',
        hover_name='country',
        projection='natural earth',
        color_continuous_scale='Reds'
    )

    # capa 2: países sin dato → gris, sin leyenda
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
        height=600,
        margin={"r":0, "t":40, "l":0, "b":0}
    )

    return fig, world_y

# -----------------------------
# Sidebar: selección de año
# -----------------------------
years = sorted(df['year'].unique())
default_year = 1950 if 1950 in years else years[len(years)//2]

st.sidebar.header("Filtros")
selected_year = st.sidebar.slider(
    "Selecciona un año",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(default_year)
)

# -----------------------------
# Mapa
# -----------------------------
st.subheader(f"🗺️ Mapa de emisiones de CO₂ en {selected_year}")
fig_map, world_y_selected = make_co2_map(df, selected_year)
st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# Gráfico de barras (Top emisores)
# -----------------------------
st.subheader(f"📊 Top países emisores en {selected_year}")

# DataFrame con países que sí tienen dato
bar_df = (
    world_y_selected[world_y_selected['co2'].notna()]
    .reset_index()[['country', 'co2']
    .sort_values('co2', ascending=False)
)

top_n = st.sidebar.number_input(
    "Nº de países en el gráfico de barras",
    min_value=5,
    max_value=30,
    value=10,
    step=1
)

bar_top = bar_df.head(top_n)

fig_bar = px.bar(
    bar_top,
    x='country',
    y='co2',
    labels={'country': 'País', 'co2': 'Emisiones CO₂'},
    title=f"Top {top_n} países emisores de CO₂ en {selected_year}"
)
fig_bar.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_bar, use_container_width=True)

# Tabla opcional
st.markdown("### 📄 Tabla de países y emisiones")
st.dataframe(bar_df, use_container_width=True)

