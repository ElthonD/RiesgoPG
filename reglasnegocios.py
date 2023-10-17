# Librerías
# ==============================================================================
import os
import nltk
import ssl
import streamlit as st
import random
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ssl._create_default_https_context = ssl._create_unverified_context
ssl._create_default_https_context = ssl._create_unverified_context
nltk.data.path.append(os.path.abspath("nltk_data"))
nltk.download('punkt')

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

def createPage():
    
    # Definir las reglas de negocio y registrar en los "intents"
    intents = [
        {
            "tag": "saludo",
            "patterns": ["Hola", "Que onda", "Hey"],
            "responses": ["Hola!,¿En que te puedo ayudar?", "Hola!,¿En que te puedo servir?", "Hey,¿Como te puedo ayudar?"]
        },
        {
            "tag": "despedida",
            "patterns": ["Adios", "Bye", "Chao", "Gracias"],
            "responses": ["Adios", "Nos leemos!", "Cuidate", "Para servirte"]
        },
        {
            "tag": "falla_mecanica",
            "patterns": ["El transporte presenta falla mecánica en zona de riesgo", "La unidad tiene falla mecánica en plena carretera federal u autopista.", "La unidad tiene falla mecánica antes de 100 km de haber iniciado recorrido"],
            "responses": ["Debes validar el contador de anomalias y si este cumple, solicitar validacion de la unidad con corredor.", "Debe validar el contador de anomalias y si este cumple, solicitar validacion de la unidad con corredor.", "Debes enviar a línea de reacción."]
        },
        {
            "tag": "vehiculo_detenido",
            "patterns": ["La unidad se encuentra detenida en zona de riesgo", "El transporte se encuentra detenido en plena carretera federal u autopista.", "La unidad tiene vehiculo detenido antes de los 100 km de recorrido."],
            "responses": ["Si el operador no responde, enviar a línea de reacción y si el operador responde, validar el contador de anomalias (2do paso) y si este cumple, solicitar validacion de la unidad con corredor.", "Si el operador no responde, enviar a línea de reacción y si el operador responde, validar el contador de anomalias (2do paso) y si este cumple, solicitar validacion de la unidad con corredor.", "Si el operador no responde, enviar a línea de reacción y si el operador responde, validar el contador de anomalias (2do paso) y si este cumple, solicitar validacion de la unidad con corredor."]
        },
        {
            "tag": "parada_no_autorizada",
            "patterns": ["Como atender una parada no autorizada", "Que hacer en una parada no autorizada", "La unidad tiene parada no autorizada"],
            "responses": ["Se comunica con el operador y le recomienda pedir paro de motor preventivo a su línea antes de terminar la llamada en IVR. Debe documentar en bitacora dicha recomendación.", "Se comunica con el operador y le recomienda pedir paro de motor preventivo a su línea antes de terminar la llamada en IVR. Debe documentar en bitacora dicha recomendación.", "Se comunica con el operador y le recomienda pedir paro de motor preventivo a su línea antes de terminar la llamada en IVR. Debe documentar en bitacora dicha recomendación."]
        },
        {
            "tag": "operador_no_responde",
            "patterns": ["El operador no responde y se encuentra en una parada no autorizada y no posiciona el GPS", "El operador no responde y tiene desvio de ruta y no posiciona el GPS", "El operador no responde y no posiciona el GPS", "El operador no responde y se tiene vehiculo detenido"],
            "responses": ["Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte.", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte.", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte."]
        },
        {
            "tag": "GPS",
            "patterns": ["El GPS no posiciona", "El GPS no da posicion", "Sin posicionamiento del GPS"],
            "responses": ["Debes validar dos (2) situaciones, 1ero si se cuenta con cuenta espejo y está no posiciona, debes enviar a línea de reacción. La 2da situación es que si se tiene cuenta espejo y está da posición, el Supervisor utilizara el status de Falla de GPS y valida que el cambio de estatus sea correcto, indicando la frecuenca de monitoreo que debe aplicar para que se documente en bitacora", "Debes validar dos (2) situaciones, 1ero si se cuenta con cuenta espejo y está no posiciona, debes enviar a línea de reacción. La 2da situación es que si se tiene cuenta espejo y está da posición, el Supervisor utilizara el status de Falla de GPS y valida que el cambio de estatus sea correcto, indicando la frecuenca de monitoreo que debe aplicar para que se documente en bitacora", "Debes validar dos (2) situaciones, 1ero si se cuenta con cuenta espejo y está no posiciona, debes enviar a línea de reacción. La 2da situación es que si se tiene cuenta espejo y está da posición, el Supervisor utilizara el status de Falla de GPS y valida que el cambio de estatus sea correcto, indicando la frecuenca de monitoreo que debe aplicar para que se documente en bitacora."]
        },
        {
            "tag": "clave_amago",
            "patterns": ["Operador da clave de amago incorrecta", "Custodia da clave de amago incorrecta", "Operador no da clave de amago", "Custodia no da clave de amago", "Operador no da clave", "Custodia no da clave"],
            "responses": ["Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte.", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte.", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte.", "Debes envíar bitácora a línea de reacción y solicitar estatus a línea de transporte"]
        }
    ]

    # Ahora preparar los intents y entrenar el modelo machine learning para el chatbot:

    # Create the vectorizer and classifier
    vectorizer = TfidfVectorizer()
    clf = LogisticRegression(random_state=0, max_iter=10000)

    # Preprocesar la data
    tags = []
    patterns = []
    for intent in intents:
        for pattern in intent['patterns']:
            tags.append(intent['tag'])
            patterns.append(pattern)

    # training the model
    x = vectorizer.fit_transform(patterns)
    y = tags
    clf.fit(x, y)

    # Saving the model
    pickle.dump(clf, open('chatbot.pkl', 'wb'))

    # Ahora escribir una función de Python para chatear con el chatbot:

    def chatbot(input_text):
        input_text = vectorizer.transform([input_text])
        tag = clf.predict(input_text)[0]
        for intent in intents:
            if intent['tag'] == tag:
                response = random.choice(intent['responses'])
                return response
 
    counter = 0
  
    st.markdown("<h3 style='text-align: left;'>Paso 6: Consultar Reglas de Negocio a Chatbot AI27</h3>", unsafe_allow_html=True)
    st.write("Bienvenido al Chatbot AI27. Escriba un mensaje y presione Entrar para indicarte la acción que debes ejecutar.")
        
    counter += 1
    user_input = st.text_input("Tú:", key=f"user_input_{counter}")

    if user_input:
        response = chatbot(user_input)
        st.text_area("Chatbot AI27:", value=response, height=100, max_chars=None, key=f"chatbot_response_{counter}")

        if response.lower() in ['adios', 'chao', 'adiós']:
            st.write("Gracias por consultar conmigo. ¡Sigamos monitoreando!")
            st.stop()

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