import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Encuesta Vocacional", page_icon="📝", layout="centered")
st.title("📝 Encuesta de participación y vocación")
st.markdown("Por favor, completa este breve formulario para ayudarnos a mejorar nuestro acompañamiento.")

# === Autenticación con Google Sheets ===
credenciales_json = st.secrets["gspread"]
if credenciales_json is None:
    st.error("❌ No se encontraron credenciales en los secretos de Streamlit Cloud.")
else:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Respuestas Encuesta Vocacional").sheet1

    with st.form("formulario_encuesta", clear_on_submit=True):
        st.subheader("🧍 Datos personales")
        col1, col2 = st.columns(2)
        with col1:
            edad = st.number_input("Edad", min_value=10, max_value=100, step=1)
            sexo = st.selectbox("Sexo", ["Hombre", "Mujer", "Prefiero no decirlo"])
        with col2:
            ciudad = st.text_input("Ciudad de residencia")
            tipo_centro = st.selectbox("Tipo de centro", ["Residencia", "Club juvenil", "Centro para mayores", "Otro"])

        conocia_a_alguien = st.radio("¿Conocías a alguien del centro antes de asistir?", ["Sí", "No"], horizontal=True)

        st.divider()
        st.subheader("📅 Proceso vocacional")
        fecha_primera_actividad = st.date_input("Fecha de tu primera actividad")
        tipo_actividad_inicial = st.selectbox("Tipo de actividad inicial", ["Círculo", "Charla", "Retiro", "Convivencia", "Plan de vida", "Otro"])
        quien_invito = st.selectbox("¿Quién te invitó?", ["Amigo", "Familiar", "Sacerdote", "Otro"])

        st.markdown("#### Frecuencia de participación (últimos 3 meses)")
        col3, col4, col5 = st.columns(3)
        with col3:
            actividades_mes_1 = st.number_input("Mes 1", min_value=0, step=1)
        with col4:
            actividades_mes_2 = st.number_input("Mes 2", min_value=0, step=1)
        with col5:
            actividades_mes_3 = st.number_input("Mes 3", min_value=0, step=1)

        acompanamiento = st.radio("¿Has recibido acompañamiento personal?", ["Sí", "No"], horizontal=True)

        st.divider()
        st.subheader("📈 Estado actual")
        pidio_admision = st.radio("¿Has pedido la admisión en la Obra?", ["Sí", "No"], horizontal=True)
        fecha_admision = st.date_input("¿Cuándo pediste la admisión?", disabled=(pidio_admision == "No"))
        sigue_asistiendo = st.radio("¿Sigues asistiendo regularmente a actividades?", ["Sí", "No"], horizontal=True)

        razon_abandono = st.text_area("Si ya no asistes, ¿por qué?", disabled=(sigue_asistiendo == "Sí"))
        actividades_valiosas = st.text_area("¿Qué actividades te parecieron más impactantes?")
        comentario = st.text_area("Comentarios adicionales")

        enviado = st.form_submit_button("🚀 Enviar respuesta")

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
        fila_str = [str(campo) if campo is not None else "" for campo in fila]
        sheet.insert_row(fila_str, index=2)

        st.success("✅ ¡Gracias! Tu respuesta ha sido registrada correctamente.")

        with st.expander("📄 Ver resumen enviado"):
            st.write("**Edad:**", edad)
            st.write("**Sexo:**", sexo)
            st.write("**Ciudad:**", ciudad)
            st.write("**Centro:**", tipo_centro)
            st.write("**Conocía a alguien:**", conocia_a_alguien)
            st.write("**Primera actividad:**", str(fecha_primera_actividad))
            st.write("**Tipo de actividad:**", tipo_actividad_inicial)
            st.write("**Quién invitó:**", quien_invito)
            st.write("**Frecuencia (Mes 1, 2, 3):**", actividades_mes_1, actividades_mes_2, actividades_mes_3)
            st.write("**Acompañamiento:**", acompanamiento)
            st.write("**Pidió admisión:**", pidio_admision)
            if pidio_admision == "Sí":
                st.write("**Fecha de admisión:**", str(fecha_admision))
            st.write("**Sigue asistiendo:**", sigue_asistiendo)
            if sigue_asistiendo == "No":
                st.write("**Razón de abandono:**", razon_abandono)
            st.write("**Actividades impactantes:**", actividades_valiosas)
            st.write("**Comentarios adicionales:**", comentario)

