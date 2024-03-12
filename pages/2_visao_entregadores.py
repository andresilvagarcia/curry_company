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

def top_delivers(df1, top_asc=False):
    df2 = df1.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)'].min().reset_index().sort_values(['City', 'Time_taken(min)'], ascending=top_asc)

    df_aux01 = df2[df2['City'] == 'Metropolitian'].head(10)
    df_aux02 = df2[df2['City'] == 'Urban'].head(10)
    df_aux03 = df2[df2['City'] == 'Semi-Urban'].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3

# ========================================================================================================
# ==================================== Inicio da Estrutura lógica do código ==============================
# ========================================================================================================

# Read DataFrame / Lendo DataFrame
df = pd.read_csv('dataset/train.csv')

# Cleaning DataFrame / Limpando DataFrame
df1 = clean_code(df)

# =========================
#  Sidebar / Barra Lateral
# =========================
st.header('Marketplace - Visão dos Entregadores')

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
    format='DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

conditions_options = st.sidebar.multiselect(
    'Quais as condições de clima',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Sunny'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Sunny'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Condições Climáticas
linhas_selecionadas = df1['Weatherconditions'].isin(conditions_options)
df1 = df1.loc[linhas_selecionadas, :]

# =========================
#    Layout Streamlit
# =========================

tab1, tab2, tab3 = st.tabs(['Visao Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            maior = df1['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior)

        with col2:
            menor = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor)

        with col3:
            melhor = df1['Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor)

        with col4:
            pior = df1['Vehicle_condition'].min()
            col4.metric('Pior Condição', pior)

    # Avaliações
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            st.dataframe(df1.groupby(['Delivery_person_ID'])['Delivery_person_Ratings'].mean().reset_index(), height=455)
        
        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            st.dataframe(df1.groupby('Road_traffic_density').agg(Delivery_mean=('Delivery_person_Ratings', 'mean'), 
                                        Delivery_STD=('Delivery_person_Ratings', 'std')).reset_index())
            
            st.markdown('##### Avaliação média por Clima')
            st.dataframe(df1.groupby(['Weatherconditions']).agg(Delivery_mean=('Delivery_person_Ratings', 'mean'), 
                                       Delivery_STD=('Delivery_person_Ratings', 'std')).reset_index())

    # Entregadores TOP
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Entregadores mais Rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top Entregadores mais Lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
