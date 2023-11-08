### Librerías

import streamlit as st
import plotly.express as px
import pandas as pd
import pickle
from dateutil.relativedelta import *
import seaborn as sns; sns.set_theme()
import numpy as np

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

def createPage():
    
    @st.cache_data(show_spinner='Actualizando Datos... Espere...', persist=True)
    def load_df():
        
        rEmbarques = './data/Salidas P&G.xlsx'
        Embarques = pd.read_excel(rEmbarques, sheet_name = "Data")
        Embarques['Inicio'] = pd.to_datetime(Embarques['Inicio'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        Embarques['Arribo'] = pd.to_datetime(Embarques['Arribo'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        Embarques['Finalización'] = pd.to_datetime(Embarques['Finalización'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        Embarques.Arribo.fillna(Embarques.Finalización, inplace=True)
        Embarques['TiempoCierreServicio'] = (Embarques['Finalización'] - Embarques['Arribo'])
        Embarques['TiempoCierreServicio'] = Embarques['TiempoCierreServicio']/np.timedelta64(1,'h')
        Embarques['TiempoCierreServicio'].fillna(Embarques['TiempoCierreServicio'].mean(), inplace=True)
        Embarques['TiempoCierreServicio'] = Embarques['TiempoCierreServicio'].astype(int)
        Embarques['Destinos'].fillna('OTRO', inplace=True)
        Embarques['Línea Transportista'].fillna('OTRO', inplace=True)
        Embarques['Duración'].fillna(Embarques['Duración'].mean(), inplace=True)
        Embarques['Duración'] = Embarques['Duración'].astype(int)
        Embarques['Mes'] = Embarques['Inicio'].apply(lambda x: x.month)
        #Embarques['Mes'] = Embarques['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        Embarques['DiadelAño'] = Embarques['Inicio'].apply(lambda x: x.dayofyear)
        Embarques['SemanadelAño'] = Embarques['Inicio'].apply(lambda x: x.weekofyear)
        Embarques['DiadeSemana'] = Embarques['Inicio'].apply(lambda x: x.dayofweek)
        Embarques['Quincena'] = Embarques['Inicio'].apply(lambda x: x.quarter)
        #Embarques['Mes'] = Embarques['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        Embarques['Origen Destino'] = Embarques['Estado Origen'] + '-' + Embarques['Estado Destino']
        #Embarques = Embarques.dropna() 
        return Embarques

    @st.cache_data(show_spinner='Procesando Datos... Espere...', persist=True)
    def ld_AR():
        rutaAR = './data/Anomalias Robos P&G.xlsx'
        AR = pd.read_excel(rutaAR, sheet_name = "Data")
        AR['Año'] = AR['Fecha'].apply(lambda x: x.year)
        AR['MesN'] = AR['Fecha'].apply(lambda x: x.month)
        AR['Mes'] = AR['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        AR['Hora'] = AR['Fecha'].apply(lambda x: x.hour)
        AR['Estadías NOM-087'] = AR['DuracionEstimada'].map(lambda x: int(x/5) if x > 5 else 0)
        #AR['Estadías NOM-087'] = np.ceil(AR['Estadías NOM-087']) 
        AR = AR.drop(['Número Envío'], axis=1)
        AR = AR.dropna()
        return AR

    def df_proba_robo(uploaded_file):
        
        input_df = pd.read_excel(uploaded_file, sheet_name = "Plantilla")
        input_df = input_df.dropna() 
        input_df['Fecha Creación'] = pd.to_datetime(input_df['Fecha Creación'], format='%Y-%m-%d %H:%M:%S',errors='coerce')
        input_df['Duración'] = input_df['Duración'].astype(int)
        input_df['Mes'] = input_df['Fecha Creación'].apply(lambda x: x.month)
        input_df['DiadelAño'] = input_df['Fecha Creación'].apply(lambda x: x.dayofyear)
        input_df['SemanadelAño'] = input_df['Fecha Creación'].apply(lambda x: x.weekofyear)
        input_df['DiadeSemana'] = input_df['Fecha Creación'].apply(lambda x: x.dayofweek)
        input_df['Quincena'] = input_df['Fecha Creación'].apply(lambda x: x.quarter)
        input_df.drop(['Fecha Creación'], axis = 'columns', inplace=True)
        input_df = input_df[['Origen Destino','Tipo Monitoreo', 'Tipo Unidad', 'Duración', 'Mes', 'DiadelAño', 'SemanadelAño', 'DiadeSemana', 'Quincena']]
        return input_df

    def resultados_proba(uploaded_file):
        
        df = pd.read_excel(uploaded_file, sheet_name = "Plantilla")
        df = df.dropna()
        df = df[['Bitácora','Origen','Destino','Tipo Monitoreo', 'Tipo Unidad']]
        df['Bitácora'] = df['Bitácora'].astype('str')
        return  df
        
    @st.cache_resource
    def load_model():
        return pickle.load(open('proba_robo_pg.pkl', 'rb'))
    
    try:
        
        #Modulo de Predictivo
        st.markdown("<h3 style='text-align: left;'>Paso 1: % Riesgo de los Servicios P&G</h3>", unsafe_allow_html=True)

        st.write(""" 
        Pasos a seguir para este módulo:
        1. Descargar archivo **"BITÁCORAS"** (Prebitácoras) de **P&G PHYSICAL** y **P&G ITRADE** del **Área de Centro de Monitoreo** del **PowerBI**, en el **Reporte CM**, sección **Prebitácoras**.
        2. Abrir archivos de Excel **"BITÁCORAS"** y **"Plantilla para Probabilidad de Robo"**.
        3. Convertir archivo descargado de prebitácora **"BITÁCORAS"** en plantilla para probabilidad de robo, para esto debe:
        + Copiar datos de la columna **"Creación"** del archivo **"BITÁCORAS"** y pegar en columna **"Fecha Creación"** del archivo **"Plantilla para Probabilidad de Robo"**.
        + Copiar datos de la columna **"Origen"** del archivo **"BITÁCORAS"** y pegar en columna **"Origen"** del archivo **"Plantilla para Probabilidad de Robo"**.
        + Copiar datos de la columna **"Destino"** del archivo **"BITÁCORAS"** y pegar en columna **"Destino"** del archivo **"Plantilla para Probabilidad de Robo"**.
        + Copiar datos de la columna **"Tipo Monitoreo"** del archivo **"BITÁCORAS"** y pegar en columna del mismo nombre en el archivo **"Plantilla para Probabilidad de Robo"**.
        + Registrar datos de la columna **"Tipo Unidad"** por cada servicio en el archivo **"Plantilla para Probabilidad de Robo"**
        + Por último, guardar archivo **"Plantilla para Probabilidad de Robo"**.
        4. Finalmente, subir archivo **"Plantilla para Probabilidad de Robo"** en la aplicación.
        """)
    
        df = load_df()    

        uploaded_file = st.file_uploader("Subir archivo Excel de pre-bitácora", type=['xlsx'])

        if uploaded_file is not None:
        
            entrada_datos = df_proba_robo(uploaded_file)

        else:
            st.warning("Se requiere subir archivo Excel")

        dsr = df.copy()
        dsr.drop(['Bitácora','Total Anomalías','Calificación','TiempoCierreServicio','Cliente','Origen','Estado Origen','Destinos','Estado Destino','Línea Transportista','Inicio','Arribo','Finalización','Tiempo Recorrido'], axis = 'columns', inplace=True)
        dsr = dsr[['Origen Destino','Tipo Monitoreo', 'Tipo Unidad', 'Duración', 'Mes', 'DiadelAño', 'SemanadelAño', 'DiadeSemana', 'Quincena', 'Robo']]
        data_sr = dsr.drop(columns=['Robo'])
        data_proba_robos = pd.concat([entrada_datos,data_sr],axis=0)

        # Codificación de características ordinales

        encode = ['Origen Destino', 'Tipo Unidad', 'Tipo Monitoreo']
        for col in encode:
            dummy = pd.get_dummies(data_proba_robos[col], prefix=col)
            data_proba_robos = pd.concat([data_proba_robos,dummy], axis=1)
            del data_proba_robos[col]

        cantidad_datos_input = len(entrada_datos)
        data_proba_robos1 = data_proba_robos[:cantidad_datos_input] # Selects only the first row (the user input data)
        #st.write(data_proba_robos1)
        
        # Leer el modelo de clasificación guardado

        #if st.button("Predict"):
            #load_clf = load_model()
            #encode = ['Origen Destino', 'Tipo Unidad', 'Tipo Monitoreo']
            #for col in encode:
                #dummy = pd.get_dummies(data_proba_robos[col], prefix=col)
                #data_proba_robos = pd.concat([data_proba_robos,dummy], axis=1)
                #del data_proba_robos[col]

            #cantidad_datos_input = len(entrada_datos)
            #data_proba_robos1 = data_proba_robos[:cantidad_datos_input] # Selects only the first row (the user input data)
            #prediction_proba = load_clf.predict_proba(data_proba_robos1)
            #st.balloons()
            #st.write(prediction_proba)
        
        #st.write(data_proba_robos1)
        
        load_clf = load_model()
        prediction_proba = load_clf.predict_proba(data_proba_robos1)

        #st.write(prediction_proba)
        
        #def predict_proba(data):
            #clf = pickle.load(open(r'proba_robo_pg.pkl', 'rb'))
            #return clf.predict_proba(data)
    
        #Aplicar modelo para hacer predicciones
        #prediction_proba = predict_proba(entrada_datos)
    
        st.markdown("<h5 style='text-align: left;'>% Riesgo de los Servicios</h5>", unsafe_allow_html=True)
        prediction_proba1 = pd.DataFrame(prediction_proba, columns = ['NO','SI'])
        entrada_datos1 = resultados_proba(uploaded_file)
        entrada_datos2 = pd.concat([entrada_datos1,prediction_proba1], axis=1)
        entrada_datos2 = entrada_datos2[['Bitácora','Origen','Destino','Tipo Monitoreo', 'Tipo Unidad', 'SI']]
        entrada_datos2 = entrada_datos2.rename(columns={'SI':'% Riesgo'})
        entrada_datos2['% Riesgo'] = round(entrada_datos2['% Riesgo'] * 100,2)
    
        col1, col2, col3 = st.columns([1,5,1])
        with col2:
            st.write(entrada_datos2)


        st.markdown("<h3 style='text-align: left;'>Paso 2: Patrón de Anomalías en Robos</h3>", unsafe_allow_html=True)
        #Modulo de Chatbot
        st.write(""" 
        La finalidad de este módulo es validar el patrón de anomalías que se han presentando en los robos de P&G dependiendo de su origen y destino. 
        """)
        df_ar = ld_AR()

        xxx1, xxx2 = st.columns(2)

        with xxx1:
            containerxxC1 = st.container()
            allxC1 = st.checkbox("Seleccionar Todos", key="FFxx")
            if allxC1:
                sorted_unique_mesxx = sorted(df_ar['EstadoOrigen'].unique())
                selected_mesxx = containerxxC1.multiselect('Origen(es):', sorted_unique_mesxx, sorted_unique_mesxx, key="FF1xx")
                df_selected_mesxx = df_ar[df_ar['EstadoOrigen'].isin(selected_mesxx)].astype(str)
            else:
                sorted_unique_mesxx = sorted(df_ar['EstadoOrigen'].unique())
                selected_mesxx = containerxxC1.multiselect('Origen(es)', sorted_unique_mesxx, key="FF1xx")
                df_selected_mesxx = df_ar[df_ar['EstadoOrigen'].isin(selected_mesxx)].astype(str)
            
        with xxx2:
            containerxxTS1 = st.container()
            allxxTS1 = st.checkbox("Seleccionar Todos", key="GGxx")
            if allxxTS1:
                sorted_unique_diaxx = sorted(df_selected_mesxx['EstadoDestino'].unique())
                selected_diaxx = containerxxTS1.multiselect('Destino(s):', sorted_unique_diaxx, sorted_unique_diaxx, key="GG1xx") 
                df_selected_diaxx = df_selected_mesxx[df_selected_mesxx['EstadoDestino'].isin(selected_diaxx)].astype(str)
            else:
                sorted_unique_diaxx = sorted(df_selected_mesxx['EstadoDestino'].unique())
                selected_diaxx = containerxxTS1.multiselect('Destino(s):', sorted_unique_diaxx, key="GG1xx") 
                df_selected_diaxx = df_selected_mesxx[df_selected_mesxx['EstadoDestino'].isin(selected_diaxx)].astype(str)

        table = pd.pivot_table(df_selected_diaxx, index = ["Cliente", "EstadoOrigen", "EstadoDestino", "Distancia", "DuracionEstimada", "Estadías NOM-087"], columns = ["Anomalía"], aggfunc = ["size"], fill_value=0)
        st.dataframe(table)
        #st.table(table)

    except UnboundLocalError as e:
        print("Seleccionar: ", e)

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

