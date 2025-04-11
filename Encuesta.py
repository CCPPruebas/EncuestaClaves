import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import os
import toml
from oauth2client.service_account import ServiceAccountCredentials

st.title("Encuesta de participación y vocación")

# === Autenticación con Google Sheets ===
# Cargar las credenciales desde el secreto TOML de Streamlit Cloud
credenciales_toml = os.getenv("gspread")  # Accede a las credenciales almacenadas en los secretos de Streamlit Cloud
if credenciales_toml is None:
    st.error("No se encontraron credenciales en los secretos de Streamlit Cloud.")
else:
    creds_dict = toml.loads(credenciales_toml)

    # Definir el alcance de la API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Crear credenciales utilizando el diccionario de las credenciales en formato JSON
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    # Autorizar y conectar a Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open("Respuestas Encuesta Vocacional").sheet1

    # === Formulario ===
    with st.form("formulario_encuesta"):
        st.header("🧍 Datos personales")
        edad = st.number_input("¿Cuál es tu edad?", min_value=10, max_value=100, step=1)
        sexo = st.selectbox("Sexo", ["Hombre", "Mujer", "Prefiero no decirlo"])
        ciudad = st.text_input("Ciudad de residencia")
        tipo_centro = st.selectbox("Tipo de centro", ["Residencia", "Club juvenil", "Centro para mayores", "Otro"])
        conocia_a_alguien = st.radio("¿Conocías a alguien del centro antes de asistir?", ["Sí", "No"])

        st.header("📅 Proceso vocacional")
        fecha_primera_actividad = st.date_input("¿Cuándo fue tu primera actividad?")
        tipo_actividad_inicial = st.selectbox("¿Qué tipo de actividad fue?",
            ["Círculo", "Charla", "Retiro", "Convivencia", "Plan de vida", "Otro"])
        quien_invito = st.selectbox("¿Quién te invitó?", ["Amigo", "Familiar", "Sacerdote", "Otro"])

        st.markdown("#### ¿Con qué frecuencia has participado en actividades?")
        actividades_mes_1 = st.number_input("Mes 1", min_value=0, step=1)
        actividades_mes_2 = st.number_input("Mes 2", min_value=0, step=1)
        actividades_mes_3 = st.number_input("Mes 3", min_value=0, step=1)
        acompanamiento = st.radio("¿Has recibido acompañamiento personal?", ["Sí", "No"])

        st.header("📈 Estado actual")
        pidio_admision = st.radio("¿Has pedido la admisión en la Obra?", ["Sí", "No"])
        fecha_admision = st.date_input("Si respondiste sí, ¿cuándo?", disabled=(pidio_admision == "No"))
        sigue_asistiendo = st.radio("¿Sigues asistiendo regularmente a actividades?", ["Sí", "No"])
        razon_abandono = st.text_area("Si ya no asistes, ¿por qué?", disabled=(sigue_asistiendo == "Sí"))
        actividades_valiosas = st.text_area("¿Qué actividades te parecieron más impactantes?")
        comentario = st.text_area("Comentarios adicionales")

        enviado = st.form_submit_button("Enviar")

    if enviado:
        fila = [
            datetime.now().isoformat(),
            edad,
            sexo,
            ciudad,
            tipo_centro,
            conocia_a_alguien,
            str(fecha_primera_actividad),
            tipo_actividad_inicial,
            quien_invito,
            actividades_mes_1,
            actividades_mes_2,
            actividades_mes_3,
            acompanamiento,
            pidio_admision,
            str(fecha_admision) if pidio_admision == "Sí" else "",
            sigue_asistiendo,
            razon_abandono if sigue_asistiendo == "No" else "",
            actividades_valiosas,
            comentario,
        ]
        sheet.append_row(fila)
        st.success("✅ ¡Respuesta guardada en Google Sheets!")
