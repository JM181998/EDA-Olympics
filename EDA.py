import streamlit as st
import pandas as pd
import folium
from matplotlib.pyplot import tight_layout
from streamlit.components.v1 import html
import matplotlib as plt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

@st.cache_data
def load_data():
    print("loading data")
    df = pd.read_csv("https://raw.githubusercontent.com/R43ed/Data_Visualization/refs/heads/main/summer.csv")
    return df

def main():
    st.title("EDA Modern Olympic Games")
    image_path = "images/image.jpg"

    # Columnas
    col1, col2 = st.columns([1, 3])  # Esto crea 2 columnas, la primera más pequeña
    
    with col1:
        image = Image.open(image_path)
        st.image(image, width=150)  # Ajusta el tamaño de la imagen según necesites

    with col2:
        st.write("""
        This Exploratory Data Analysis (EDA) focuses on the Olympic Games from 1986 to 2012, examining the performance of athletes and countries based on gold, silver, and bronze medals. 
        It aims to identify trends and patterns in medal distribution, athlete success, and country performance across multiple OG. The analysis looks at which athletes and nations dominated, as well as how the competition and medal distribution evolved over the years.
        """)
        st.write("""
        Key insights from the dataset include identifying top-performing athletes, the dominance of certain countries in specific events, and shifts in medal rankings across different Olympics. The study also explores trends in the overall number of medals, highlighting changes in the OG' structure and how countries and athletes have improved or changed their strategies over time.
        """)
    
    df = load_data()
    with st.expander(label="Original dataset - Summer Olympics", expanded=False):
        st.dataframe(df)
    # Filtro por años
    min_year, max_year = st.slider(label="Select Year Range",
                                   min_value=int(df['Year'].min()),
                                   max_value=int(df['Year'].max()),
                                   value=(1896, 2012),
                                   step=4)
    df = df[(df['Year'] >= min_year) & (df['Year'] <= max_year)]
    # Filtro por deporte
    selected_sports = st.multiselect(label="Select Sport/s",
                                     options=["All"] + sorted(df['Sport'].dropna().unique().tolist()),
                                     default=["All"])
    if "All" not in selected_sports:
        df = df[df['Sport'].isin(selected_sports)]
    # Filtro por disciplina
    if len(selected_sports) > 0 and "All" not in selected_sports:
        unique_disciplines = ["All"] + sorted(df['Event'].dropna().unique().tolist())
        selected_disciplines = st.multiselect(label="Select Disciplines",
                                              options=unique_disciplines,
                                              default=["All"])
        if "All" not in selected_disciplines:
            df = df[df['Event'].isin(selected_disciplines)]
    # Filtro por género
    gender = st.radio(label="Select Gender",
                      options=["Both", "Men", "Women"],
                      index=0,
                      horizontal=True)
    if gender == "Men":
        df = df[df['Gender'] == 'Men']
    elif gender == "Women":
        df = df[df['Gender'] == 'Women']
    #Filtro por medallas
    selected_medals = st.radio(label="Select Medals",
                               options=["All", "Gold", "Silver", "Bronze"],
                               index=0,
                               horizontal=True)
    if selected_medals == "Gold":
        df = df[df['Medal'] == 'Gold']
    elif selected_medals == "Silver":
        df = df[df['Medal'] == 'Silver']
    elif selected_medals == "Bronze":
        df = df[df['Medal'] == 'Bronze']

    st.write(f"Your Data Selection has {df.shape[0]} rows and {df.shape[1]} columns. Activate this dropdown if you want to see the resulting Dataframe.")
    with st.expander(label="Filtered Dataset", expanded=False):
        st.dataframe(df)

    # Gráfico 1: Distribución de medallas por país
    conteo_medallas = df[df['Medal'].notnull()].groupby(['Country', 'Medal']).size().unstack(fill_value=0)
    conteo_medallas['Total'] = conteo_medallas.sum(axis=1)

    for medal in ['Gold', 'Silver', 'Bronze']:
        if medal not in conteo_medallas.columns:
            conteo_medallas[medal] = 0

    top_10_paises = conteo_medallas.sort_values(by='Total', ascending=False).head(10)
    
    top_10_plot = top_10_paises[['Gold', 'Silver', 'Bronze']].reset_index().melt(id_vars='Country', 
                                                                                value_vars=['Gold', 'Silver', 'Bronze'], 
                                                                                var_name='Medal', 
                                                                                value_name='Count')
    fig = px.bar(top_10_plot, 
                x='Country', 
                y='Count', 
                color='Medal',
                color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': 'brown'},
                labels={'Count': 'Number of Medals'},
                height=400)

    st.markdown("### Top 10 of your selection")
    st.write("This chart shows the medals of the most winning country according with the data provided. Is the Top 10 Countries by Medal Count filtered by your selection.")
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico 2: Folium de los ganadores
    st.markdown("### Map of the winners of your selection")
    st.write("This map shows the winners of your previous selection with the data provided.")
    mapa = folium.Map(location=[20, -10], zoom_start=1.5)
    paises = df["Country"].unique()

    coordenadas = {
        'AFG': [33.939, 67.710],  # Afganistán
        'AHO': [12.178, 61.551],  # Países Bajos Antillas (Bonaire)
        'ALG': [28.034, 1.660],  # Argelia
        'ANZ': [4.383, 18.657],  # Angola
        'ARG': [-38.416, -63.617],  # Argentina
        'ARM': [40.069, 45.038],  # Armenia
        'AUS': [-25.274, 133.775],  # Australia
        'AUT': [47.516, 14.550],  # Austria
        'AZE': [40.143, 47.577],  # Azerbaiyán
        'BAH': [25.034, -77.396],  # Bahamas
        'BAR': [13.194, -59.543],  # Barbados
        'BDI': [-3.373, 29.919],  # Burundi
        'BEL': [50.850, 4.352],  # Bélgica
        'BER': [32.308, -64.751],  # Bermudas
        'BLR': [53.900, 27.567],  # Bielorrusia
        'BOH': [48.020, 66.924],  # Bosnia y Herzegovina
        'BOT': [-22.328, 24.685],  # Botsuana
        'BRA': [-14.235, -51.925],  # Brasil
        'BRN': [4.535, 114.728],  # Brunéi
        'BUL': [42.734, 25.486],  # Bulgaria
        'BWI': [17.190, -62.140],  # Islas Vírgenes Británicas
        'CAN': [56.130, -106.347],  # Canadá
        'CHI': [-33.449, -70.669],  # Chile
        'CHN': [35.862, 104.195],  # China
        'CIV': [7.540, -5.547],  # Costa de Marfil
        'CMR': [3.848, 11.502],  # Camerún
        'COL': [4.571, -74.297],  # Colombia
        'CRC': [9.749, -83.753],  # Costa Rica
        'CRO': [45.100, 15.200],  # Croacia
        'CUB': [21.522, -77.781],  # Cuba
        'CYP': [35.126, 33.430],  # Chipre
        'CZE': [49.818, 15.473],  # Chequia
        'DEN': [56.264, 9.502],  # Dinamarca
        'DJI': [11.825, 42.590],  # Yibuti
        'DOM': [18.736, -70.163],  # República Dominicana
        'ECU': [-1.831, -78.183],  # Ecuador
        'EGY': [26.820, 30.803],  # Egipto
        'ERI': [15.179, 39.782],  # Eritrea
        'ESP': [40.464, -3.749],  # España
        'EST': [58.595, 25.014],  # Estonia
        'ETH': [9.145, 40.490],  # Etiopía
        'EUA': [37.090, -95.713],  # Estados Unidos
        'EUN': [54.526, 15.255],  # Unión Europea
        'FIN': [61.924, 25.748],  # Finlandia
        'FRA': [46.603, 1.888],  # Francia
        'FRG': [51.166, 10.452],  # Alemania (República Federal)
        'GAB': [-0.804, 11.609],  # Gabón
        'GBR': [55.378, -3.436],  # Reino Unido
        'GDR': [51.166, 10.452],  # Alemania (República Democrática)
        'GEO': [42.315, 43.357],  # Georgia
        'GER': [51.166, 10.452],  # Alemania
        'GHA': [7.946, -1.023],  # Ghana
        'GRE': [39.074, 21.824],  # Grecia
        'GRN': [12.515, -86.221],  # Granada
        'GUA': [13.909, -90.231],  # Guatemala
        'GUY': [4.860, -58.930],  # Guyana
        'HAI': [18.971, -72.285],  # Haití
        'HKG': [22.319, 114.169],  # Hong Kong
        'HUN': [47.162, 19.503],  # Hungría
        'INA': [-0.789, 113.921],  # Indonesia
        'IND': [20.594, 78.963],  # India
        'IOP': [6.000, 100.000],  # Territorio Británico del Océano Índico
        'IRI': [32.428, 53.688],  # Irán
        'IRL': [53.413, -8.244],  # Irlanda
        'IRQ': [33.223, 43.679],  # Irak
        'ISL': [64.963, -19.021],  # Islandia
        'ISR': [31.046, 34.852],  # Israel
        'ISV': [18.336, -64.896],  # Islas Vírgenes de EE. UU.
        'ITA': [41.872, 12.567],  # Italia
        'JAM': [18.110, -77.298],  # Jamaica
        'JPN': [36.205, 138.253],  # Japón
        'KAZ': [48.020, 66.924],  # Kazajistán
        'KEN': [-1.292, 36.822],  # Kenia
        'KGZ': [41.204, 74.766],  # Kirguistán
        'KOR': [35.908, 127.767],  # Corea del Sur
        'KSA': [23.886, 45.079],  # Arabia Saudita
        'KUW': [29.376, 47.977],  # Kuwait
        'LAT': [56.880, 24.603],  # Letonia
        'LIB': [33.855, 35.862],  # Líbano
        'LTU': [55.169, 23.881],  # Lituania
        'LUX': [49.612, 6.130],  # Luxemburgo
        'MAR': [31.792, -7.093],  # Marruecos
        'MAS': [4.211, 101.976],  # Malasia
        'MDA': [47.412, 28.370],  # Moldavia
        'MEX': [23.634, -102.553],  # México
        'MGL': [46.863, 103.847],  # Mongolia
        'MKD': [41.609, 21.745],  # Macedonia del Norte
        'MNE': [42.709, 19.374],  # Montenegro
        'MOZ': [-18.666, 35.530],  # Mozambique
        'MRI': [-20.348, 57.552],  # Mauricio
        'NAM': [-22.958, 18.490],  # Namibia
        'NED': [52.133, 5.291],  # Países Bajos
        'NGR': [9.082, 8.675],  # Nigeria
        'NIG': [17.608, 8.082],  # Níger
        'NOR': [60.472, 8.469],  # Noruega
        'NZL': [-40.901, 174.886],  # Nueva Zelanda
        'PAK': [30.375, 69.345],  # Pakistán
        'PAN': [8.538, -80.782],  # Panamá
        'PAR': [-23.443, -58.444],  # Paraguay
        'PER': [-9.190, -75.015],  # Perú
        'PHI': [12.880, 121.774],  # Filipinas
        'POL': [51.919, 19.145],  # Polonia
        'POR': [39.400, -8.225],  # Portugal
        'PRK': [40.340, 127.510],  # Corea del Norte
        'PUR': [18.221, -66.590],  # Puerto Rico
        'QAT': [25.355, 51.184],  # Catar
        'ROU': [45.943, 24.967],  # Rumanía
        'RSA': [-30.560, 22.938],  # Sudáfrica
        'RU1': [55.756, 37.618],  # Rusia
        'RUS': [55.756, 37.618],  # Rusia
        'SCG': [44.017, 21.006],  # Serbia y Montenegro
        'SEN': [14.497, -14.452],  # Senegal
        'SGP': [1.352, 103.820],  # Singapur
        'SIN': [1.352, 103.820],  # Singapur
        'SLO': [46.151, 14.996],  # Eslovenia
        'SRB': [44.017, 21.006],  # Serbia
        'SRI': [7.873, 80.772],  # Sri Lanka
        'SUD': [12.863, 30.218],  # Sudán
        'SUI': [46.818, 8.228],  # Suiza
        'SUR': [3.919, -56.028],  # Surinam
        'SVK': [48.669, 19.699],  # Eslovaquia
        'SWE': [60.128, 18.644],  # Suecia
        'SYR': [34.802, 38.997],  # Siria
        'TAN': [-6.369, 34.889],  # Tanzania
        'TCH': [49.818, 15.473],  # Checoslovaquia
        'TGA': [-21.179, -175.198],  # Tonga
        'THA': [15.870, 100.993],  # Tailandia
        'TJK': [38.861, 71.276],  # Tayikistán
        'TOG': [7.447, 1.702],  # Togo
        'TPE': [25.033, 121.565],  # Taiwán
        'TRI': [10.692, -61.223],  # Trinidad y Tobago
        'TTO': [10.692, -61.223],  # Trinidad y Tobago
        'TUN': [33.887, 9.537],  # Túnez
        'TUR': [38.964, 35.243],  # Turquía
        'UAE': [23.424, 53.848],  # Emiratos Árabes Unidos
        'UGA': [1.373, 32.290],  # Uganda
        'UKR': [48.379, 31.166],  # Ucrania
        'URS': [55.756, 37.618],  # Unión Soviética
        'URU': [-32.965, -56.013],  # Uruguay
        'USA': [37.090, -95.713],  # Estados Unidos
        'UZB': [41.378, 64.585],  # Uzbekistán
        'VEN': [6.424, -66.590],  # Venezuela
        'VIE': [21.029, 105.854],  # Vietnam
        'YUG': [44.017, 21.006],  # Yugoslavia
        'ZAM': [-13.134, 27.849],  # Zambia
        'ZIM': [-19.015, 29.155],  # Zimbabue
        'ZZX': [0.000, 0.000],  # Coordenadas no definidas
        'nan': [None, None]  # Valor nulo
    }

    for pais in paises:
        if pais in coordenadas:
            cantidad_medallas = df[df["Country"] == pais].shape[0]

            folium.Marker(
                location=coordenadas[pais],
                popup=f"{pais} - {cantidad_medallas} medals",
            ).add_to(mapa)

    mapa_html = mapa._repr_html_()
    html(mapa_html, width=1000, height=500)

if __name__ == "__main__":
    main()
    df2 = pd.read_csv("https://raw.githubusercontent.com/R43ed/Data_Visualization/refs/heads/main/summer.csv")
    
    # Gráfico 3: Participación a lo largo de los años
    st.markdown("### Athlete Participation Over the Years")
    st.write("This chart shows the number of athletes participating in the Olympics each year and how participation has changed over time.")
    participation_by_year = df2.groupby('Year').size().reset_index(name='Athletes')
    fig = px.line(participation_by_year, x='Year', y='Athletes', 
                labels={'Year': 'Year', 'Athletes': 'Number of Athletes'},
                line_shape='linear', markers=True)
    fig.update_traces(line=dict(color='orange'))
    st.plotly_chart(fig)
    fig.update_layout(width=900, height=225)

    # Gráfico 4: Distribución de eventos por deporte
    st.markdown("### Events Distribution by Sport")
    st.write("This bar chart visualizes the distribution of Olympic events across different sports over the years.")
    event_count_by_sport = df2['Sport'].value_counts().reset_index()
    event_count_by_sport.columns = ['Sport', 'Event Count']

    fig = px.bar(
        event_count_by_sport, 
        x='Event Count', 
        y='Sport', 
        orientation='h', 
        color='Event Count',
        color_continuous_scale='Viridis'
    )

    st.plotly_chart(fig, use_container_width=True)
