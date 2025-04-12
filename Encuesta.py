import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime

# Autenticación del Admin (para el login)
admin_password = st.secrets["admin"]["password"]

# Función para verificar las credenciales
def check_credentials(password):
    if password == admin_password:
        return True
    return False

# Panel de login para admin
st.title("Login de Administrador")

# Ingresar contraseña del admin
password = st.text_input("Contraseña", type="password")

# Si el usuario hace clic en el botón "Iniciar sesión"
if st.button("Iniciar sesión"):
    if check_credentials(password):
        st.success("¡Acceso concedido! Bienvenido al panel de administración.")
        
        # Aquí mostrarás las respuestas de la encuesta
        st.write("### Panel de Administración")
        
        # Conectar con Google Sheets usando las credenciales de gspread
        credenciales_json = st.secrets["gspread"]
        if credenciales_json:
            # Configuración para la conexión con Google Sheets
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Respuestas Encuesta Vocacional").sheet1

            # Mostrar las respuestas de la encuesta
            respuestas = sheet.get_all_records()  # Obtener todas las respuestas
            st.write("### Respuestas de la Encuesta")
            st.dataframe(respuestas)  # Mostrar respuestas en formato tabla
    else:
        st.error("Credenciales incorrectas. Intenta nuevamente.")
        
# Formulario de encuesta (parte pública)
else:
    st.title("Encuesta de participación y vocación")

    # === Autenticación con Google Sheets ===
    credenciales_json = st.secrets["gspread"]
    if credenciales_json is None:
        st.error("No se encontraron credenciales en los secretos de Streamlit Cloud.")
    else:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
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
            fila_str = [str(campo) if campo is not None else "" for campo in fila]

            # Inserta la fila en la segunda posición, justo debajo de los encabezados
            sheet.insert_row(fila_str, index=2)

            st.success("✅ ¡Respuesta guardada en la primera columna correctamente!")

