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
import numpy as np

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

def distance(df1, fig):
    if fig == False:
        mean_distance = df1['Distance'] = df1[['Restaurant_latitude', 
                'Restaurant_longitude', 
                'Delivery_location_latitude', 
                'Delivery_location_longitude']].apply(lambda x: haversine(
                    (x['Restaurant_latitude'], 
                        x['Restaurant_longitude']), 
                        (x['Delivery_location_latitude'], 
                        x['Delivery_location_longitude'])), axis=1)
        mean_distance = np.round(df1['Distance'].mean(), 2)
        return mean_distance
    else:
        df1['Distance'] = df1[['Restaurant_latitude', 
                        'Restaurant_longitude', 
                        'Delivery_location_latitude', 
                        'Delivery_location_longitude']].apply(lambda x: haversine(
                            (x['Restaurant_latitude'], 
                            x['Restaurant_longitude']), 
                            (x['Delivery_location_latitude'], 
                                x['Delivery_location_longitude'])), axis=1)

        mean_distance = df1.groupby('City')['Distance'].mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=mean_distance['City'], values=mean_distance['Distance'], pull=[0, 0.1, 0])])
        return fig

def avg_std_time_graph(df1):
    st.markdown('##### Tempo Médio de Entrega por Cidade')
    df_aux = df1.groupby('City')[['Time_taken(min)']].agg(Tempo_medio=('Time_taken(min)', 'mean'), 
                                                Desvio_padrao=('Time_taken(min)', 'std')).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['Tempo_medio'],
                        error_y=dict(type='data', array=df_aux['Desvio_padrao'])))

    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1):
    df_aux = df1.groupby(['City', 'Road_traffic_density'])[['Time_taken(min)']].agg(Tempo_medio=('Time_taken(min)', 'mean'),
                                                            Desvio_padrao=('Time_taken(min)', 'std')).reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Tempo_medio',
                    color='Desvio_padrao', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['Desvio_padrao']))
    return fig

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
st.header('Marketplace - Visão Restaurantes')

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
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            qtd_entregadores = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', qtd_entregadores)

        with col2:
            mean_distance = distance(df1, fig=False)
            col2.metric('A distância média', mean_distance)            

        with col3:
            medio = np.round(df1[df1['Festival'] == 'Yes']['Time_taken(min)'].mean())
            col3.metric('Tempo médio de Entrega c/ Festival', medio)

        with col4:
            medio = np.round(df1[df1['Festival'] == 'Yes']['Time_taken(min)'].std())
            col4.metric('Desvio padrão médio de Entrega c/ Festival', medio)

        with col5:
            medio = np.round(df1[df1['Festival'] == 'No']['Time_taken(min)'].mean())
            col5.metric('Tempo médio de Entrega s/ Festival', medio)

        with col6:
            medio = np.round(df1[df1['Festival'] == 'No']['Time_taken(min)'].std())
            col6.metric('Desvio padrão médio de Entrega s/ Festival', medio)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('##### O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')
            st.dataframe(df1.groupby(['City', 'Type_of_order'])[['Time_taken(min)']].agg(Tempo_medio=('Time_taken(min)', 'mean'),
                                                                Desvio_padrao=('Time_taken(min)', 'std')).reset_index(), use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns(2)

        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
