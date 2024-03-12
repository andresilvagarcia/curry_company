import streamlit as st
from PIL import Image

st.set_page_config(
page_title="Home",
page_icon="📈"
)

#img_path = (r'C:\Users\Andre\Desktop\Comunidade DS\FTC Analisando dados com Python\logo.jpg')
image= Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.write('# Curry Company Growth Dashboard')
st.markdown(
    """
    Gorwth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão do Entregador:
        - Acompanhamento dos indicaroes semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimentos dos restaurantes.
    ### Ask for Help
    - Time de Data Science no Discord
        - @onevodkaa
"""
)