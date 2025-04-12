import streamlit as st
import pandas as pd
import gspread
from datetime import datetime, date
from oauth2client.service_account import ServiceAccountCredentials

# === Configuración general ===
st.set_page_config(page_title="Encuesta Vocacional", page_icon="🧭", layout="centered")

# === Encabezado con logo ===
st.markdown("""
<div style='text-align: center'>
    <img src='https://i.scdn.co/image/ab6765630000ba8aec1c485bc9de786d9e65b3f6' width='100' style='border-radius: 50%;'/>
    <h1 style='margin-bottom: 0;'>Encuesta Vocacional</h1>
    <p style='margin-top: 0; font-size: 16px;'>Tu participación es valiosa para entender mejor tu camino de formación.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# === Autenticación con Google Sheets ===
credenciales_json = st.secrets["gspread"]
if credenciales_json is None:
    st.error("❌ No se encontraron credenciales en los secretos de Streamlit Cloud.")
else:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Respuestas Encuesta Vocacional").sheet1

    # === Estado actual previo al formulario ===
    st.subheader("📌 Estado actual")
    sigue_asistiendo = st.radio("¿Sigues asistiendo regularmente a actividades?", ["Sí", "No"], horizontal=True)
    st.markdown("---")

    # === Formulario ===
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
        col3, col4 = st.columns(2)
        with col3:
            fecha_primera_actividad = st.date_input("Fecha de tu primera actividad")
        with col4:
            tipo_actividad_inicial = st.selectbox("Tipo de actividad inicial", ["Círculo", "Charla", "Retiro", "Convivencia", "Plan de vida", "Otro"])

        quien_invito = st.selectbox("¿Quién te invitó?", ["Amigo", "Familiar", "Sacerdote", "Otro"])

        st.markdown("#### 📆 Participación reciente (últimos 3 meses)")
        col5, col6, col7 = st.columns(3)
        with col5:
            actividades_mes_1 = st.number_input("Mes 1", min_value=0, step=1)
        with col6:
            actividades_mes_2 = st.number_input("Mes 2", min_value=0, step=1)
        with col7:
            actividades_mes_3 = st.number_input("Mes 3", min_value=0, step=1)

        acompanamiento = st.radio("¿Has recibido acompañamiento personal?", ["Sí", "No"], horizontal=True)

        st.divider()

        st.subheader("📥 Decisiones vocacionales")
        pidio_admision = st.radio("¿Has pedido la admisión en la Obra?", ["Sí", "No"], horizontal=True)
        fecha_admision = st.date_input("¿Cuándo pediste la admisión?", disabled=(pidio_admision == "No"))

        razon_abandono = ""
        if sigue_asistiendo == "No":
            razon_abandono = st.text_area("¿Por qué ya no asistes?")

        actividades_valiosas = st.text_area("🎯 ¿Qué actividades te impactaron más?")
        comentario = st.text_area("💬 Comentarios adicionales")

        st.markdown("---")
        enviado = st.form_submit_button("📨 Enviar respuesta")

    # === Guardar en Google Sheets ===
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

        st.balloons()
        st.success("✅ ¡Gracias! Tu respuesta ha sido registrada correctamente.")

        with st.expander("📄 Ver resumen de tu respuesta"):
            st.markdown(f"""
            - **Edad:** {edad}  
            - **Sexo:** {sexo}  
            - **Ciudad:** {ciudad}  
            - **Centro:** {tipo_centro}  
            - **Conocía a alguien:** {conocia_a_alguien}  
            - **Primera actividad:** {str(fecha_primera_actividad)}  
            - **Tipo de actividad:** {tipo_actividad_inicial}  
            - **Quién invitó:** {quien_invito}  
            - **Frecuencia (Mes 1, 2, 3):** {actividades_mes_1}, {actividades_mes_2}, {actividades_mes_3}  
            - **Acompañamiento:** {acompanamiento}  
            - **Pidió admisión:** {pidio_admision}  
            {"- **Fecha admisión:** " + str(fecha_admision) if pidio_admision == "Sí" else ""}
            - **Sigue asistiendo:** {sigue_asistiendo}  
            {"- **Razón de abandono:** " + razon_abandono if sigue_asistiendo == "No" else ""}
            - **Actividades impactantes:** {actividades_valiosas}  
            - **Comentarios adicionales:** {comentario}
            """)

# === Pie de página ===
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; font-size: 0.85em; color: gray;'>
        🛡️ Esta encuesta es confidencial. Los datos serán utilizados únicamente con fines de análisis vocacional.<br>
        © {date.today().year} Centro de Formación Vocacional · Todos los derechos reservados.<br>
        📄 <a href="https://tu-sitio.com/politica-de-privacidad" target="_blank" style="color: gray; text-decoration: underline;">Política de privacidad</a> · 
        🔢 Versión del formulario: 1.0
    </div>
    """,
    unsafe_allow_html=True
)
