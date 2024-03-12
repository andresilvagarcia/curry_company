# Libraries / Bibliotecas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

# =========================
# Functions / Funções
#==========================
def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudaça do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (Remoção do texto da variável numérica)

        Imput: Dataframe
        Output: Dataframe    
    """
    # Filtrar linhas onde 'Delivery_person_Age' não é NaN
    selected_lines = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[selected_lines, :].copy()

    # 1. Convertendo a coluna Age de texto para número
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype('int')

    # 2. Convertendo a coluna Rating de texto para número decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype('float')

    # 3. Convertendo a coluna Date de texto para Datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. Convertendo a coluna Multiple Delivery para Int
    selected_lines = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[selected_lines, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype('int')

    # 5. Removendo NaN das colunas
    selected_lines = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[selected_lines, :].copy()
    selected_lines = df1['City'] != 'NaN '
    df1 = df1.loc[selected_lines, :].copy()
    selected_lines = df1['Type_of_vehicle'] != 'NaN '
    df1 = df1.loc[selected_lines, :].copy()
    selected_lines = df1['Festival'] != 'NaN '
    df1 = df1.loc[selected_lines, :].copy()

    # 6. Removendo espaços dentro de strings
    df1 = df1.reset_index(drop=True)
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # 7. Limpando a coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def order_metric(df1):
    df_aux = df1[['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    # Desenhar o gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig

def traffic_order_share(df1):
    df_aux = df1[['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['Entregas_percent'] = df_aux['ID'] / df_aux['ID'].sum()
    # Gráfico de pizza
    fig = px.pie(df_aux, values='Entregas_percent', names='Road_traffic_density')
    return fig

def traffic_order_city(df1):
    df_aux = df1[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    # Gráfico de bolhas
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df1): 
    # Criar coluna de semana
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    # Quantidade de pedidos por semana
    df_aux = df1[['ID', 'Week_of_year']].groupby('Week_of_year').count().reset_index()
    # Grafico de linhas
    fig = px.line(df_aux, x='Week_of_year', y='ID')
    return fig

def order_share_by_week(df1):
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux01 = df1[['ID', 'Week_of_year']].groupby('Week_of_year').count().reset_index()
    df_aux02 = df1[['Delivery_person_ID', 'Week_of_year']].groupby('Week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # Desenhando gráfico de linhas
    fig = px.line(df_aux, x='Week_of_year', y='Order_by_deliver')
    return fig

def country_maps(df1):
    df_aux = df1[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Desenhando gráfico de mapa/pinos
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)
    return None

# ========================================================================================================
# ==================================== Inicio da Estrutura lógica do código ==============================
# ========================================================================================================

# Read DataFrame / Lendo DataFrame
df = pd.read_csv(r'..\dataset\train.csv')

# Cleaning DataFrame / Limpando DataFrame
df1 = clean_code(df)

# =========================
#  Sidebar / Barra Lateral
# =========================
st.header('Marketplace - Visão Cliente')

#image_path = r'C:\Users\Andre\Desktop\Comunidade DS\FTC Analisando dados com Python\logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# =========================
#    Layout Streamlit
# =========================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)        
        
        with col2:
            fig = traffic_order_city(df1)
            st.header(' Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)                

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)            

    with st.container():
        fig = order_share_by_week(df1)
        st.markdown('# Order Share by Week')
        st.plotly_chart(fig, use_container_width=True)        

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
