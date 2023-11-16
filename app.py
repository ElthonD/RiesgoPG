import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import start, probabilidadestatica, mapasligero, reglasnegocios  # Importar páginas acá

 #### Páginas
path_favicon = './img/favicon1.png'
im = Image.open(path_favicon)
st.set_page_config(page_title='AI27 P&G', page_icon=im, layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#v_menu=["Inicio", "Riesgo de los Servicios", "Mapas Planner", "Carga de Trabajo", "Reglas de Negocio"]
v_menu=["Inicio", "Riesgo de los Servicios", "Mapas Planner", "Reglas de Negocio"]

selected = option_menu(
    menu_title=None,  # required
    options=["Inicio", "Riesgo de los Servicios", "Mapas Planner", "Reglas de Negocio"],  # required 
    icons=["house", "percent", "map", "list-ol"],  # optional
    #icons=["house", "percent", "map", "graph-up", "list-ol"],  # optional
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
    styles={
        "container": {"padding": "10px", "background-color": "#fafafa"},
        "icon": {"font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "salmon"},
        "nav-link-selected": {"background-color": "tomato"},
    }
    )

if selected=="Inicio":
    start.createPage()

if selected=="Riesgo de los Servicios":
    probabilidadestatica.createPage()

if selected=="Mapas Planner":
    mapasligero.createPage()

#if selected=="Carga de Trabajo":
    #pronostico.createPage()

if selected=="Reglas de Negocio":
    reglasnegocios.createPage()
