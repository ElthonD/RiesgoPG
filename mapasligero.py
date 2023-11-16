### Librerías

import streamlit as st
import pandas as pd
import folium
from folium import plugins
from folium.plugins import HeatMapWithTime
from streamlit_folium import folium_static
from dateutil.relativedelta import *
import seaborn as sns; sns.set_theme()
import numpy as np
import requests

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

def createPage():
    
    @st.cache_data(show_spinner='Cargando Datos... Espere...', persist=True)
    def load_AN():
        rutaA = r'./data/Anomalias P&G.xlsx'
        Anomalia = pd.read_excel(rutaA, sheet_name = "Data")
        Anomalia = Anomalia.drop(['Número Envío'], axis=1)
        Anomalia = Anomalia.dropna()
        Anomalia.Fecha = pd.to_datetime(Anomalia.Fecha, format='%Y-%m-%d %H:%M:%S')
        Anomalia['Año'] = Anomalia.Fecha.apply(lambda x: x.year)
        Anomalia['MesN'] = Anomalia['Fecha'].apply(lambda x: x.month)
        Anomalia['Mes'] = Anomalia['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        Anomalia['Semana'] = Anomalia.Fecha.apply(lambda x: x.week)
        Anomalia['DiaSemana'] = Anomalia.Fecha.apply(lambda x: x.dayofweek)
        Anomalia['Dia'] = Anomalia.Fecha.apply(lambda x: x.day)
        Anomalia['Hora'] = Anomalia.Fecha.apply(lambda x: x.hour)
        return Anomalia
   
    @st.cache_data(show_spinner='Cargando Datos... Espere...', persist=True)
    def load_HR():

        rutaA = r'./data/Historico de Robos P&G.xlsx'
        Robos = pd.read_excel(rutaA, sheet_name = "Data")
        Robos = Robos.drop(['Operadores','CM', 'Línea Reacción'], axis=1)
        Robos['Fecha'] = Robos['Fecha'].dt.strftime('%m/%d/%Y')
        Robos['Fecha'] = pd.to_datetime(Robos['Fecha'], format="%Y/%m/%d", infer_datetime_format=True)
        Robos['Año'] = Robos.Fecha.apply(lambda x: x.year)
        Robos['MesN'] = Robos['Fecha'].apply(lambda x: x.month)
        Robos['Mes'] = Robos['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        Robos['Dia'] = Robos.Fecha.apply(lambda x: x.day)
        Robos['Fecha y Hora'] = pd.to_datetime(Robos['Fecha y Hora'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        Robos = Robos.dropna()

        return Robos
    
    def load_patrullas():
    
        path = r'./data/Patrullas.xlsx'
        patrullas = pd.read_excel(path, sheet_name = "Patrullas")
    
        return patrullas
    
    def load_nPatrullas():
    
        path = r'./data/Patrullas.xlsx'
        patrullas = pd.read_excel(path, sheet_name = "Dedicados")
    
        return patrullas

    def GenerarMapaBase(Centro=[20.5223, -99.8883], zoom=8):
        MapaBase = folium.Map(location=Centro, control_scale=True, zoom_start=zoom)
        return MapaBase

    def map_coropleta_fol(df):
    
        #geojson_url = './data/mexicoHigh.json'
        geojson_url = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json'
        mx_estados_geo = requests.get(geojson_url).json()

        MapaMexico1 = GenerarMapaBase()

        FeatRobo = folium.FeatureGroup(name='Robos')
        #Recorrer marco de datos y agregar cada punto de datos al grupo de marcadores
        Latitudes2 = df['Latitud'].to_list()
        Longitudes2 = df['Longitud'].to_list()
        Popups2 = df['Cliente'].to_list()
        Popups3 = df['Tipo evento'].to_list()
        Popups4 = df['Estado'].to_list()
        Popups5 = df['Origen'].to_list()
        Popups6 = df['Destinos'].to_list()
        Popups7 = df['Línea transportista'].to_list()
        Popups8 = df['Fecha y Hora'].to_list()

        #Agregar Bases al Mapa
        path = './img/P&G_logo.png'
        iconPG = folium.features.CustomIcon(path, icon_size=(30,30))
    
        #Crear Marcadores de las Bases y agregarlos al Mapa

        #for lat2, long2, pop2, pop3, pop4, pop5, pop6, pop7, pop8 in list(zip(Latitudes2, Longitudes2, Popups2, Popups3, Popups4, Popups5, Popups6, Popups7, Popups8)):
            #fLat2 = float(lat2)
            #fLon2 = float(long2)
            #folium.Marker(location=[fLat2,fLon2], popup= [pop2,pop3,pop4, pop5, pop6, pop7, pop8], icon=iconPG).add_to(FeatRobo)
  
        for lat2, long2, pop2, pop3, pop4, pop5, pop6, pop7, pop8 in list(zip(Latitudes2, Longitudes2, Popups2, Popups3, Popups4, Popups5, Popups6, Popups7, Popups8)):
            fLat2 = float(lat2)
            fLon2 = float(long2)
            if pop3 == "Consumado":
                folium.Circle(
                    radius=200,
                    location=[fLat2,fLon2],
                    popup= [pop2,pop3,pop4, pop5, pop6, pop7, pop8],
                    fill=False,
                    color="darkred").add_to(FeatRobo)
            else:
                folium.Circle(
                    radius=200,
                    location=[fLat2,fLon2],
                    popup= [pop2,pop3,pop4, pop5, pop6, pop7, pop8],
                    fill=False,
                    color="darkgreen").add_to(FeatRobo)
        
        df1 = pd.DataFrame(pd.value_counts(df['Estado']))
        df1 = df1.reset_index()
        df1.rename(columns={'index':'Estado','Estado':'Total'},inplace=True)

        folium.Choropleth(
            geo_data=mx_estados_geo,
            name="Mapa Coropleta",
            data=df1,
            columns=["Estado", "Total"],
            key_on="feature.properties.name",
            fill_color="OrRd",
            fill_opacity=0.7,
            line_opacity=.1,
            legend_name="Total de Robos",
            nan_fill_color = "White",
            show=True,
            overlay=True,
            Highlight= True,
            ).add_to(MapaMexico1)

        MapaMexico1.add_child(FeatRobo)
        folium.LayerControl().add_to(MapaMexico1)
        #Agregar Botón de Pantalla Completa 
        plugins.Fullscreen(position="topright").add_to(MapaMexico1)

        #Mostrar Mapa
        folium_static(MapaMexico1, width=1370)

    def mapa_calor(df, df2, df1, df4):
    
        #Crear mapa y desplegarlo
        MapaMexico = GenerarMapaBase()
        marcadores = plugins.MarkerCluster().add_to(MapaMexico)

        #Agregar Patrullas al Mapa
        path = './img/Car.png'

        for i in range(len(df1)):
            patrullas = ''
            for info in df1.loc[i,['Tramo','Distancia del Tramo','Tiempo Recorrido']]:
                item = '<{0}>{1}</{0}>'.format('li',info)
                patrullas += item
    
                html=f"""
                <h5>{df1.iloc[i]['Nombre']}</h5>
                <ul>
                {patrullas}
                </ul>
                """
                iframe = folium.IFrame(html=html, width=200, height=150)
                popup = folium.Popup(iframe, max_width=200)
                folium.Marker(
                location=[df1.iloc[i]['Latitud'], df1.iloc[i]['Longitud']],
                popup=popup,
                icon= folium.features.CustomIcon(path, icon_size=(25,25))
                ).add_to(MapaMexico)
    
        #Agregar Nuevas Patrullas al Mapa
        path1 = './img/Car1.png'

        for i in range(len(df4)):  #df3 Dataframe nuevas patrullas
            patrullas1 = ''
            for info in df4.loc[i,['Tramo','Distancia del Tramo','Tiempo Recorrido']]:
                item1 = '<{0}>{1}</{0}>'.format('li',info)
                patrullas1 += item1
    
                html1=f"""
                <h5>{df4.iloc[i]['Nombre']}</h5>
                <ul>
                {patrullas1}
                </ul>
                """
                iframe1 = folium.IFrame(html=html1, width=200, height=150)
                popup1 = folium.Popup(iframe1, max_width=200)
                folium.Marker(
                    location=[df4.iloc[i]['Latitud'], df4.iloc[i]['Longitud']],
                    popup=popup1,
                    icon= folium.features.CustomIcon(path1, icon_size=(25,25))
                ).add_to(MapaMexico)

        #Recorrer marco de datos y agregar cada punto de datos al grupo de marcadores
        Latitudes2 = df2['Latitud'].to_list()
        Longitudes2 = df2['Longitud'].to_list()
        Popups2 = df2['Tipo evento'].to_list()
        Popups3 = df2['Cliente'].to_list()
    
        for lat2, long2, pop2, pop3 in list(zip(Latitudes2, Longitudes2, Popups2, Popups3)):
            fLat2 = float(lat2)
            fLon2 = float(long2)
            if pop2 == "Consumado":
                folium.Circle(
                    radius=200,
                    location=[fLat2,fLon2],
                    popup= [pop2,pop3],
                    fill=False,
                    color="darkred").add_to(marcadores)
            else:
                folium.Circle(
                    radius=200,
                    location=[fLat2,fLon2],
                    popup= [pop2,pop3],
                    fill=False,
                    color="darkgreen").add_to(marcadores)
    
        df1 = df.copy()
        df1['Contar'] = 1
        df_hora1 = []

        for hour in df1.Hora.sort_values().unique():
            df_hora1.append(df1.loc[df1.Hora == hour, ['Latitud', 'Longitud', 'Contar']].groupby(['Latitud', 'Longitud']).sum().reset_index().values.tolist())
    
        HeatMapWithTime(df_hora1, radius=5, gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}, min_opacity=0.5, max_opacity=0.8, use_local_extrema=True).add_to(MapaMexico)

        #Agregar Botón de Pantalla Completa 
        plugins.Fullscreen(position="topright").add_to(MapaMexico)

        #Mostrar Mapa
        folium_static(MapaMexico, width=1370)

    try:
        
        st.markdown("<h4 style='text-align: left;'>Paso 3: Consultar Histórico de Robos P&G (Planner) </h4>", unsafe_allow_html=True)
        st.write(""" 
        La finalidad de este módulo es consultar el histórico de robos de P&G. Pasos a seguir para este módulo:
        1. Seleccionar el **Mes** del cuál desea obtener información en el mapa. Seleccionando el checkbox, puede seleccionar todos los meses del año que presenten robos de P&G.
        2. Seleccionar el **Dia** del cuál desea obtener información en el mapa. Seleccionando el checkbox, puede seleccionar todos los días del año que presenten robos de P&G.
        3. El resultado indica:
        + Icono con el Logo de P&G donde se presentan todos los robos y ubicados por Estados de la República Mexicana.
        + Información sobre el robo (Origen, Destinos, Estado, Tipo evento (Recuperado/Consumado), Mes, Día, Hora).
        """)

        df3 = load_HR()
        st.write(f"Este módulo contiene información histórica de los robos de P&G desde **{df3.Mes.values[0]} {df3.Año.values[0].astype(int)}** a **{df3.Mes.values[-1]} {df3.Año.values[-1].astype(int)}** :")

        x1, x2 = st.columns(2)

        with x1:
            containerC1 = st.container()
            allC1 = st.checkbox("Seleccionar Todos", key="FF")
            if allC1:
                sorted_unique_mes = sorted(df3['Mes'].unique())
                selected_mes = containerC1.multiselect('Mes(es):', sorted_unique_mes, sorted_unique_mes, key="FF1")
                df_selected_mes = df3[df3['Mes'].isin(selected_mes)].astype(str)
            else:
                sorted_unique_mes = sorted(df3['Mes'].unique())
                selected_mes = containerC1.multiselect('Mes(es)', sorted_unique_mes, key="FF1")
                df_selected_mes = df3[df3['Mes'].isin(selected_mes)].astype(str)
            
        with x2:
            containerTS1 = st.container()
            allTS1 = st.checkbox("Seleccionar Todos", key="GG")
            if allTS1:
                sorted_unique_dia = sorted(df_selected_mes['Día'].unique())
                selected_dia = containerTS1.multiselect('Día(s):', sorted_unique_dia, sorted_unique_dia, key="GG1") 
                df_selected_dia = df_selected_mes[df_selected_mes['Día'].isin(selected_dia)].astype(str)
            else:
                sorted_unique_dia = sorted(df_selected_mes['Día'].unique())
                selected_dia = containerTS1.multiselect('Día(s):', sorted_unique_dia, key="GG1") 
                df_selected_dia = df_selected_mes[df_selected_mes['Día'].isin(selected_dia)].astype(str)
    
        st.markdown("<h5 style='text-align: left;'>Mapa de Robos</h5>", unsafe_allow_html=True)

        mapa_coropleta = map_coropleta_fol(df_selected_dia)

        st.markdown("<h4 style='text-align: left;'>Paso 4: Zonas de Riesgo </h4>", unsafe_allow_html=True)
        st.write(""" 
        La finalidad de este módulo es visualizar la frecuencia de robos por días y horas por las zonas de riesgo en el comportamiento histórico por meses de los robos de P&G. 
        """)

        df4 = df3.copy()

        xx1, xx2, xx3 = st.columns(3)

        with xx1:
            containerxTS1 = st.container()
            allxTS1 = st.checkbox("Seleccionar Todos", key="GGgx")
            if allxTS1:
                sorted_unique_mesx = sorted(df4['Mes'].unique())
                selected_mesx = containerxTS1.multiselect('Mes(es):', sorted_unique_mesx, sorted_unique_mesx, key="GGg1x") 
                df_selected_mesx = df4[df4['Mes'].isin(selected_mesx)].astype(str)
            else:
                sorted_unique_mesx = sorted(df4['Mes'].unique())
                selected_mesx = containerxTS1.multiselect('Mes(es):', sorted_unique_mesx, key="GGg1x") 
                df_selected_mesx = df4[df4['Mes'].isin(selected_mesx)].astype(str)

        with xx2:
            containerxTS2 = st.container()
            allxTS2 = st.checkbox("Seleccionar Todos", key="GGx")
            if allxTS2:
                sorted_unique_diax = sorted(df_selected_mesx['DíaSem'].unique())
                selected_diax = containerxTS2.multiselect('Día(s):', sorted_unique_diax, sorted_unique_diax, key="GG1x") 
                df_selected_diax = df_selected_mesx[df_selected_mesx['DíaSem'].isin(selected_diax)].astype(str)
            else:
                sorted_unique_diax = sorted(df_selected_mesx['DíaSem'].unique())
                selected_diax = containerxTS2.multiselect('Día(s):', sorted_unique_diax, key="GG1x") 
                df_selected_diax = df_selected_mesx[df_selected_mesx['DíaSem'].isin(selected_diax)].astype(str)

        with xx3:
            containerxC1 = st.container()
            allxC1 = st.checkbox("Seleccionar Todos", key="FFx")
            if allxC1: 
                sorted_unique_horax = sorted(df_selected_diax['Hora'].unique())
                selected_horax = containerxC1.multiselect('Hora(s):', sorted_unique_horax, sorted_unique_horax, key="FF1x")
                df_selected_horax = df_selected_diax[df_selected_diax['Hora'].isin(selected_horax)].astype(str)
            else:
                sorted_unique_horax = sorted(df_selected_diax['Hora'].unique())
                selected_horax = containerxC1.multiselect('Hora(s)', sorted_unique_horax, key="FF1x")
                df_selected_horax = df_selected_diax[df_selected_diax['Hora'].isin(selected_horax)].astype(str)

        cxx1, cxx2, cxx3 = st.columns([1,1,1])

        with cxx2:
            
            df_tramos = df_selected_horax.groupby(['Tramo']).size()
            df_tramos1 = pd.DataFrame(df_tramos)
            df_tramos1.reset_index(drop = False, inplace = True)
            df_tramos1 = df_tramos1.rename(columns={'Tramo':'Tramos', 0:'Total'})
            df_tramos1.sort_values(by=['Total'], inplace=True, ascending=False)
            #st.write(df_tramos1)
            st.table(df_tramos1)
        #st.markdown("<h4 style='text-align: left;'>Paso 4: Mapa de Calor </h4>", unsafe_allow_html=True)
        #st.write(""" 
        #La finalidad de este módulo es visualizar las patrullas en campo junto con el comportamiento histórico de anomalías de P&G. 
        #Está visualización permite de acuerdo a la probabiliad de robo estática y el mapa de robos administrar los recursos en campo para la preparación y movilización de los mismos.
        #""")
        #st.markdown("<h5 style='text-align: left;'>Mapa de Calor</h5>", unsafe_allow_html=True)

        #df_anomalias = load_AN()
        #df_hr = df_selected_dia.copy()
        #df_patrullas = load_patrullas()
        #df_nuevaspatrullas = load_nPatrullas()

        #xx1, xx2 = st.columns(2)

        #with xx1:
            #containerxC1 = st.container()
            #allxC1 = st.checkbox("Seleccionar Todos", key="FFx")
            #if allxC1: 
                #sorted_unique_mesx = sorted(df_anomalias['Mes'].unique())
                #selected_mesx = containerxC1.multiselect('Mes(es):', sorted_unique_mesx, sorted_unique_mesx, key="FF1x")
                #df_selected_mesx = df_anomalias[df_anomalias['Mes'].isin(selected_mesx)].astype(str)
            #else:
                #sorted_unique_mesx = sorted(df_anomalias['Mes'].unique())
                #selected_mesx = containerxC1.multiselect('Mes(es)', sorted_unique_mesx, key="FF1x")
                #df_selected_mesx = df_anomalias[df_anomalias['Mes'].isin(selected_mesx)].astype(str)
            
        #with xx2:
            #containerxTS1 = st.container()
            #allxTS1 = st.checkbox("Seleccionar Todos", key="GGx")
            #if allxTS1:
                #sorted_unique_diax = sorted(df_selected_mesx['Dia'].unique())
                #selected_diax = containerxTS1.multiselect('Día(s):', sorted_unique_diax, sorted_unique_diax, key="GG1x") 
                #df_selected_diax = df_selected_mesx[df_selected_mesx['Dia'].isin(selected_diax)].astype(str)
            #else:
                #sorted_unique_diax = sorted(df_selected_mesx['Dia'].unique())
                #selected_diax = containerxTS1.multiselect('Día(s):', sorted_unique_diax, key="GG1x") 
                #df_selected_diax = df_selected_mesx[df_selected_mesx['Dia'].isin(selected_diax)].astype(str)

    
        #mapacalor = mapa_calor(df_selected_diax, df_hr, df_patrullas, df_nuevaspatrullas)

    except ZeroDivisionError as e:
        print("Seleccionar: ", e)
    
    except KeyError as e:
        print("Seleccionar: ", e)

    except ValueError as e:
        print("Seleccionar: ", e)
    
    except IndexError as e:
        print("Seleccionar: ", e)

     # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    return True

