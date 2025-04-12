import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import altair as alt

st.set_page_config(page_title="Panel Admin", page_icon="🔒", layout="wide")

# === Estilo encabezado ===
st.markdown("""
<div style='text-align: center'>
    <img src='https://i.scdn.co/image/ab6765630000ba8aec1c485bc9de786d9e65b3f6' width='80' style='border-radius: 50%;'/>
    <h1 style='margin-bottom: 0;'>Panel Administrativo</h1>
    <p style='margin-top: 0; font-size: 16px;'>Visualización de resultados de la encuesta vocacional</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# === Login simple ===
if "acceso_admin" not in st.session_state:
    st.session_state.acceso_admin = False

if not st.session_state.acceso_admin:
    password_input = st.text_input("Introduce la contraseña de administrador:", type="password")
    if st.button("Acceder"):
        if password_input == st.secrets["admin"]["password"]:
            st.session_state.acceso_admin = True
            st.success("✅ Acceso concedido")
        else:
            st.error("❌ Contraseña incorrecta")
    st.stop()

# === Acceso autorizado ===

# === Autenticación Google Sheets ===
credenciales_json = st.secrets["gspread"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
client = gspread.authorize(creds)
sheet = client.open("Respuestas Encuesta Vocacional").sheet1
datos = sheet.get_all_records()
df = pd.DataFrame(datos)

# === Panel ===
st.subheader("📊 Estadísticas generales")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total de respuestas", len(df))
    st.metric("Edad promedio", round(df["edad"].mean(), 1))
    st.metric("Participantes que pidieron admisión", df[df["pidio_admision"] == "Sí"].shape[0])

with col2:
    sexo_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("sexo:N", title="Sexo"),
        y=alt.Y("count():Q", title="Cantidad"),
        color="sexo:N"
    ).properties(title="Distribución por sexo", width=300, height=200)
    st.altair_chart(sexo_chart, use_container_width=True)

    actividad_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("tipo_actividad_inicial:N", title="Tipo de actividad"),
        y=alt.Y("count():Q", title="Cantidad"),
        color="tipo_actividad_inicial:N"
    ).properties(title="Tipo de primera actividad", width=300, height=200)
    st.altair_chart(actividad_chart, use_container_width=True)

# === Tabla de datos ===
st.subheader("📄 Datos completos")
st.dataframe(df, use_container_width=True)

# === Descarga ===
st.download_button("⬇️ Descargar respuestas en Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="respuestas.csv", mime="text/csv")

# === Pie de página ===
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; font-size: 0.85em; color: gray;'>
        🔐 Acceso privado · Uso exclusivo de administradores autorizados.<br>
        © {date.today().year} Centro de Formación Vocacional · Todos los derechos reservados.
    </div>
    """,
    unsafe_allow_html=True
)
