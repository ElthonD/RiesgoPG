### Librerías

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import *
import seaborn as sns; sns.set_theme()
import numpy as np

# Modelado y Forecasting
# ==============================================================================
#from fbprophet import Prophet
from prophet import Prophet

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

def createPage():
    
    @st.cache_data(show_spinner='Cargando Datos... Espere...', persist=True)
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
        Embarques['DiadelAño'] = Embarques['Inicio'].apply(lambda x: x.dayofyear)
        Embarques['SemanadelAño'] = Embarques['Inicio'].apply(lambda x: x.weekofyear)
        Embarques['DiadeSemana'] = Embarques['Inicio'].apply(lambda x: x.dayofweek)
        Embarques['Quincena'] = Embarques['Inicio'].apply(lambda x: x.quarter)
        #Embarques['Mes'] = Embarques['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        Embarques['Origen Destino'] = Embarques['Estado Origen'] + '-' + Embarques['Estado Destino']
        #Embarques = Embarques.dropna() 
        return Embarques


    @st.cache_data(show_spinner='Cargando Datos... Espere...', persist=True)
    def load_df_lr():
        rutaER = './data/Envios a LR P&G.xlsx'
        ER = pd.read_excel(rutaER, sheet_name = "Data")
        ER['COMENTARIOS ENVIO'] = ER['COMENTARIOS ENVIO'].fillna('SIN COMENTARIOS')
        ER['ALERTAS'] = ER['ALERTAS'].fillna('SIN ALERTAS')
        ER['COMENTARIOS ENVIO'] = ER['COMENTARIOS ENVIO'].astype(str)
        ER['ALERTAS'] = ER['ALERTAS'].astype(str)
        ER['CLIENTE'] = ER['CLIENTE'].astype(str)
        ER['FECHA ENVIO'] = pd.to_datetime(ER['FECHA ENVIO'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        ER['Año'] = ER['FECHA ENVIO'].apply(lambda x: x.year)
        ER['MesN'] = ER['FECHA ENVIO'].apply(lambda x: x.month)
        ER['Mes'] = ER['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
        ER['Dia'] = ER['FECHA ENVIO'].apply(lambda x: x.day)
        ER['Hora'] = ER['FECHA ENVIO'].apply(lambda x: x.hour)
        ER['LATITUD'] = ER['LATITUD'].astype(float)
        ER['LONGITUD'] = ER['LONGITUD'].astype(float)
        ER['LATITUD'].fillna(ER['LATITUD'].mean(), inplace=True)
        ER['LONGITUD'].fillna(ER['LONGITUD'].mean(), inplace=True)
        ER = ER.dropna()

        return ER

    st.cache_data(ttl=3600)
    def crear_df(df):

        df['Duración'] = df['Duración'].astype(int)
        df1 = pd.DataFrame(data = df, index = np.repeat(df.index, abs(df['Duración'])))
        df2 = pd.DataFrame(pd.concat(
                [
                    df.iloc[:,0].reindex(
                    pd.date_range(idx, periods=abs(row["Duración"]), freq="H"),
                    )
                    for idx, row in df.iterrows()
                ]).ffill())
    
        df2["HorasActiva"] = df2.index
        df2.drop(['Bitácora'], axis = 'columns', inplace=True)        
        df2.reset_index(drop=True, inplace=True)
        df2['HorasActiva'] = [d.time() for d in df2['HorasActiva']]
        df2['HorasActiva'] = pd.to_timedelta(df2['HorasActiva'].astype(str))
        df1.reset_index(drop=True, inplace=True)
        df1['Inicio'] = pd.to_datetime(df1['Inicio'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')
        dfs = pd.concat([df1, df2], axis=1)
        dfs["FHBitacora"] = dfs["Inicio"] + dfs["HorasActiva"]
        #dfs["FHBitacora"] = dfs["Inicio"].astype(str) + dfs["HorasActiva"].astype(str)
        #dfs["FHBitacora"] = dt.datetime.strptime(dfs["Inicio"],'%Y-%m-%d %H:%M:%S') + dt.datetime.strptime(dfs["HorasActiva"],'%Y-%m-%d %H:%M:%S')
        # Reindexar el dfframe
        #dfs["FHBitacora"] =  pd.to_datetime(dfs["FHBitacora"], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        dfs.index = dfs["FHBitacora"] 
        #Eliminar Columnas que no son parte del Análisis
        dfs.drop(['Cliente', 'Tipo Monitoreo','Total Anomalías','Calificación','Origen','Destinos','Línea Transportista','Tipo Unidad','Inicio','Arribo','Finalización','Tiempo Recorrido','Duración', 'Robo', 'Mes'], axis = 'columns', inplace=True)
        #Remuestreo
        dfs = dfs.Bitácora.resample('H').count()
        #Generar dfFrame
        dfs = pd.DataFrame(dfs)
        return dfs

    def envios_lr(df):
        df = pd.DataFrame(data = df)
        df.reset_index(inplace=True, drop=True)
        df1 = pd.DataFrame(df)
        df1['FECHA ENVIO'] = pd.to_datetime(df1['FECHA ENVIO'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        #Reindexar DataFrame
        df1.index = df1["FECHA ENVIO"]
        df1.drop(['FOLIO','COMENTARIOS ENVIO','ALERTAS'], axis = 'columns', inplace=True)
        #Remuestreo
        dfRE = df1.BITACORA.resample('H').count()
        #Dataframe final
        dfd = pd.DataFrame(dfRE)
        return dfd
    
    def carga_trabajo_cm(df):
            
        #Para CM
        sr_data3 = go.Scatter(x = df['Fecha'],
                        y=df['Servicios'],
                        opacity=0.8,
                        yaxis = 'y1',
                        marker= dict(color = "blue"),
                        hoverinfo = 'text',
                        name='Servicios/Hora',
                        text= [f'Servicios/Hora: {x:.0f}' for x in df['Servicios']]
                        )
    
        sr_data4 = go.Scatter(x = df['Fecha'],
                        y=df['Personal Requerido'],
                        line=go.scatter.Line(color='red', width = 3),
                        opacity=0.8,
                        yaxis = 'y2',
                        name='Personal Requerido/Hora',
                        text= [f'Personal Requerido: {x:.0f}' for x in df['Personal Requerido']]
                        )

        # Create a layout with interactive elements and two yaxes
        layout = go.Layout(height=700, width=1400, font=dict(size=10),
                   plot_bgcolor="#FFF",
                   xaxis=dict(showgrid=False, title='Fecha',
                                        # Range selector with buttons
                                         rangeselector=dict(
                                             # Buttons for selecting time scale
                                             buttons=list([
                                                 # 1 month
                                                 dict(count=1,
                                                      label='1m',
                                                      step='month',
                                                      stepmode='backward'),
                                                 # 1 week
                                                 dict(count=7,
                                                      label='1w',
                                                      step='day',
                                                      stepmode='todate'),
                                                 # 1 day
                                                 dict(count=1,
                                                      label='1d',
                                                      step='day',
                                                      stepmode='todate'),
                                                 # 12 hours
                                                 dict(count=12,
                                                      label='12h',
                                                      step='hour',
                                                      stepmode='backward'),
                                                 # Entire scale
                                                 dict(step='all')
                                             ])
                                         ),
                                         # Sliding for selecting time window
                                         rangeslider=dict(visible=True),
                                         # Type of xaxis
                                         type='date'),
                   yaxis=dict(showgrid=False, title='Servicios Activos/Hora', color='red', side = 'left'),
                   # Add a second yaxis to the right of the plot
                   yaxis2=dict(showgrid=False, title='Personal Requerido/Hora', color='blue',
                                          overlaying='y1',
                                          side='right')
                   )
        fig = go.Figure(data=[sr_data3, sr_data4], layout=layout)
        st.plotly_chart(fig)
    
    def carga_trabajo_lr(df1):
            
        #Para LR
        sr_data5 = go.Scatter(x = df1['Fecha'],
                        y=df1['Envios a LR'],
                        opacity=0.8,
                        yaxis = 'y1',
                        marker= dict(color = "blue"),
                        hoverinfo = 'text',
                        name='Envios a LR/Hora',
                        text= [f'Envios a LR/Hora: {x:.0f}' for x in df1['Envios a LR']]
                        )
            
        sr_data6 = go.Scatter(x = df1['Fecha'],
                        y=df1['Personal Requerido'],
                        line=go.scatter.Line(color='red', width = 2),
                        opacity=0.8,
                        yaxis = 'y2',
                        name='Personal Requerido/Hora',
                        text= [f'Personal Requerido: {x:.0f} por Hora' for x in df1['Personal Requerido']]
                        )

        # Create a layout with interactive elements and two yaxes
        layout = go.Layout(height=700, width=1400, font=dict(size=10),
                   plot_bgcolor="#FFF",
                   xaxis=dict(showgrid=False, title='Fecha',
                                        # Range selector with buttons
                                         rangeselector=dict(
                                             # Buttons for selecting time scale
                                             buttons=list([
                                                 # 1 month
                                                 dict(count=1,
                                                      label='1m',
                                                      step='month',
                                                      stepmode='backward'),
                                                 # 1 week
                                                 dict(count=7,
                                                      label='1w',
                                                      step='day',
                                                      stepmode='todate'),
                                                 # 1 day
                                                 dict(count=1,
                                                      label='1d',
                                                      step='day',
                                                      stepmode='todate'),
                                                 # 12 hours
                                                 dict(count=12,
                                                      label='12h',
                                                      step='hour',
                                                      stepmode='backward'),
                                                 # Entire scale
                                                 dict(step='all')
                                             ])
                                         ),
                                         # Sliding for selecting time window
                                         rangeslider=dict(visible=True),
                                         # Type of xaxis
                                         type='date'),
                   yaxis=dict(showgrid=False, title='Envios a LR/Hora', color='red', side = 'left'),
                   # Add a second yaxis to the right of the plot
                   yaxis2=dict(showgrid=False, title='Personal Requerido/Hora', color='blue',
                                          overlaying='y1',
                                          side='right')
                   )
        fig = go.Figure(data=[sr_data5, sr_data6], layout=layout)
        st.plotly_chart(fig)

    try:
        
        df = load_df()    

        #Modulo de Predictivo
        st.markdown("<h3 style='text-align: left;'>Paso 5: Determinar Carga de Trabajo</h3>", unsafe_allow_html=True)
    
        st.write(""" 
        La finalidad de este módulo es determinar el personal necesario para evitar desfases de atención tanto en Centro de Monitoreo como en Línea de Reacción. Pasos a seguir para este módulo:
        1. Seleccionar en el slider el **número de días** a pronosticar, esto puede ser de un (1) día a 30 días.
        2. Se inicia el proceso de cálculo del pronostico (Puede tomar de 2 a 5 minutos el proceso de cálculo del pronóstico).
        3. El resultado indica:
            + **"Pronóstico"**, indica la cantidad de servicios activos por hora.
            + **"Personal Requerido"**, indica la cantidad de monitoristas necesario para responder a la operación y evitar desfases de atención en Centro de Monitoreo P&G y Línea de Reacción.
        """)
 
        a1, a2, a3 = st.columns([1,10,1])
        with a2:
            n_dias = st.slider('Predicciones (Días):', 1, 30)

        d1, d2 = st.columns(2)
        with d1:
        
            #### Módulo Pronóstico Centro de Monitoreo
            df_cm = df.copy()   
            st.markdown("<h5 style='text-align: left;'>Predicción de Servicios Activos por Hora en Centro de Monitoreo P&G</h5>", unsafe_allow_html=True)
            #n_dias = st.slider('Predicciones (Días):', 1, 30)
            period = n_dias*24
            #data2 = crear_df(data1)
            data2 = crear_df(df_cm)
            data2['Fecha'] = data2.index
            data2 = data2[['Fecha','Bitácora']]
            data2.columns = ['Fecha', 'Servicios']

            # Predict forecast with Prophet.
            df_train = data2[['Fecha','Servicios']]
            df_train = df_train.rename(columns={"Fecha": "ds", "Servicios": "y"})

            m = Prophet()
            m.fit(df_train)
            future = m.make_future_dataframe(periods=period, freq='H')
            forecast = m.predict(future)
            dfer = pd.DataFrame(data = forecast)
            dfr1 = dfer[['ds', 'yhat']]
            dfr1 = dfr1.rename(columns={"ds": "Fecha", "yhat": "Servicios"})
            #dfr1['Servicios'] = np.where(dfr1['Servicios'] < 0, 0, dfr1['Servicios'])
            dfr1['Servicios'] = abs(dfr1['Servicios'])
            dfr1['Servicios'] = dfr1['Servicios'].apply(np.ceil)
            dfr1['Servicios'] = dfr1['Servicios'].astype(int)
            dfr1['Personal Requerido'] = np.ceil(dfr1['Servicios'].astype(int)/20)
            st.dataframe(dfr1.tail(period))

        with d2:
            df1 = load_df_lr()
            #### Módulo Pronóstico de Línea de Reacción
            df_lr = df1.copy()
            df2 = envios_lr(df_lr)
            st.markdown("<h5 style='text-align: left;'>Predicción de Envios a LR de P&G por Hora</h5>", unsafe_allow_html=True)
            #n_dias = st.slider('Predicciones (Días):', 1, 30)
            period1 = n_dias*24
            df2['FECHA ENVIO'] = df2.index
            df2 = df2[['FECHA ENVIO','BITACORA']]
            df2.columns = ['Fecha', 'Envios a LR']

            # Predict forecast with Prophet.
            df_train1 = df2[['Fecha','Envios a LR']]
            df_train1 = df_train1.rename(columns={"Fecha": "ds", "Envios a LR": "y"})

            m1 = Prophet()
            m1.fit(df_train1)
            future1 = m1.make_future_dataframe(periods=period1, freq='H')
            forecast1 = m.predict(future1)
            dfer1 = pd.DataFrame(data = forecast1)
            dfr2 = dfer1[['ds', 'yhat']]
            dfr2 = dfr2.rename(columns={"ds": "Fecha", "yhat": "Envios a LR"})
            #dfr1['Servicios'] = np.where(dfr1['Servicios'] < 0, 0, dfr1['Servicios'])
            dfr2['Envios a LR'] = abs(dfr2['Envios a LR'])
            dfr2['Envios a LR'] = dfr2['Envios a LR'].apply(np.ceil)
            dfr2['Envios a LR'] = dfr2['Envios a LR'].astype(int)
            dfr2['Personal Requerido'] = np.ceil(dfr2['Envios a LR'].astype(int)/4)
            st.dataframe(dfr2.tail(period))


        st.markdown("<h5 style='text-align: left;'>Gráfica de Predicción de los Servicios Activos por Hora</h5>", unsafe_allow_html=True)

        grafica1 = carga_trabajo_cm(dfr1)

        st.markdown("<h5 style='text-align: left;'>Gráfica de Predicción Envios a Línea de Reacción por Hora</h5>", unsafe_allow_html=True)

        grafica2 = carga_trabajo_lr(dfr2)

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

