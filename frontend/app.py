# ============================================================
# PROYECTO SENTINEL
# FASE IV - FRONTEND CON STREAMLIT
# Detección de fraude en reclamaciones de seguros
# ============================================================

import os
import json
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Sentinel - Detección de Fraude",
    page_icon="🛡️",
    layout="wide"
)

# URL del backend FastAPI
# La variable de entorno permitirá utilizar Docker después.
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

# ============================================================
# DIAGNÓSTICO TEMPORAL DE CONEXIÓN
# ============================================================
st.write("URL utilizada por Streamlit:", API_URL)

BASE_DIR = Path(__file__).resolve().parent.parent

EJEMPLO_PATH = (
    BASE_DIR / "tests" / "ejemplo_reclamacion.json"
)


# ============================================================
# 2. FUNCIONES DE COMUNICACIÓN CON FASTAPI
# ============================================================

def consultar_api(endpoint):

    respuesta = requests.get(
        f"{API_URL}{endpoint}",
        timeout=15
    )

    respuesta.raise_for_status()

    return respuesta.json()


def predecir_reclamacion(datos):

    respuesta = requests.post(
        f"{API_URL}/predict",
        json={"datos": datos},
        timeout=30
    )

    respuesta.raise_for_status()

    return respuesta.json()


# ============================================================
# 3. CARGAR RECLAMACIÓN DE EJEMPLO
# ============================================================

def cargar_ejemplo():

    with open(
        EJEMPLO_PATH,
        "r",
        encoding="utf-8"
    ) as archivo:

        contenido = json.load(archivo)

    return contenido["datos"]


# ============================================================
# 4. ENCABEZADO
# ============================================================

st.title("🛡️ Sentinel")

st.subheader(
    "Detección de posibles fraudes en reclamaciones de seguros"
)

st.info(
    "Prototipo educativo basado en Machine Learning. "
    "Las alertas requieren revisión humana y no "
    "constituyen una decisión automática sobre la reclamación."
)


# ============================================================
# 5. VERIFICAR CONEXIÓN CON FASTAPI
# ============================================================

try:

    salud = consultar_api("/health")

    if not salud.get("modelo_cargado", False):
        st.error("La API está disponible, pero el modelo no está cargado.")
        st.stop()

    caracteristicas = consultar_api("/features")

    variables = caracteristicas["variables"]

    st.success(
        "Conexión establecida correctamente con Sentinel API."
    )

except requests.RequestException as error:

    st.error(
        "No fue posible conectar con FastAPI. "
        "Verifica que el backend esté ejecutándose."
    )

    st.caption(f"Detalle técnico: {error}")

    st.stop()


# ============================================================
# 6. MOSTRAR INFORMACIÓN DEL MODELO
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Modelo",
        caracteristicas["modelo"]
    )

with col2:
    st.metric(
        "Variables",
        len(variables)
    )

with col3:
    st.metric(
        "Estado de la API",
        "Activa"
    )


# ============================================================
# 7. PREPARAR DATOS DEL FORMULARIO
# ============================================================

try:

    ejemplo = cargar_ejemplo()

except (FileNotFoundError, KeyError, json.JSONDecodeError):

    st.error(
        "No se encontró un archivo de reclamación "
        "de ejemplo válido en la carpeta tests."
    )

    st.stop()


st.divider()

st.header("Datos de la reclamación")

st.write(
    "Introduce o modifica los valores de la reclamación "
    "que deseas analizar."
)


# ============================================================
# 8. GENERAR FORMULARIO DINÁMICO
# ============================================================

datos_formulario = {}

with st.form("formulario_sentinel"):

    columnas = st.columns(2)

    for indice, variable in enumerate(variables):

        valor_original = ejemplo.get(variable)

        with columnas[indice % 2]:

            # Identificar valores booleanos
            if isinstance(valor_original, bool):

                valor = st.checkbox(
                    variable,
                    value=valor_original
                )

            # Identificar valores enteros
            elif isinstance(valor_original, int):

                valor = st.number_input(
                    variable,
                    value=valor_original,
                    step=1
                )

            # Identificar valores decimales
            elif isinstance(valor_original, float):

                valor = st.number_input(
                    variable,
                    value=valor_original
                )

            # Variables categóricas
            else:

                valor = st.text_input(
                    variable,
                    value=(
                        ""
                        if valor_original is None
                        else str(valor_original)
                    )
                )

            datos_formulario[variable] = valor

    boton_predecir = st.form_submit_button(
        "Analizar reclamación",
        use_container_width=True
    )


# ============================================================
# 9. EJECUTAR PREDICCIÓN
# ============================================================

if boton_predecir:

    with st.spinner(
        "Analizando reclamación con Sentinel..."
    ):

        try:

            resultado = predecir_reclamacion(
                datos_formulario
            )

            # Conservar el resultado en la sesión
            st.session_state["resultado"] = resultado

        except requests.HTTPError as error:

            st.error(
                "La API rechazó la solicitud. "
                "Revisa los valores introducidos."
            )

            if error.response is not None:
                st.code(error.response.text)

            st.session_state.pop("resultado", None)

        except requests.RequestException:

            st.error(
                "No fue posible completar la predicción. "
                "Comprueba la conexión con FastAPI."
            )

            st.session_state.pop("resultado", None)


# ============================================================
# 10. MOSTRAR RESULTADOS
# ============================================================

if "resultado" in st.session_state:

    resultado = st.session_state["resultado"]

    st.divider()

    st.header("Resultado del análisis")

    probabilidad = resultado["probabilidad_fraude"]

    umbral = resultado["umbral_alerta"]

    alerta = resultado["alerta"]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Puntuación estimada de fraude",
            f"{probabilidad * 100:.2f}%"
        )

    with col2:

        st.metric(
            "Umbral de alerta",
            f"{umbral * 100:.2f}%"
        )

    st.progress(
        min(max(float(probabilidad), 0.0), 1.0)
    )

    if alerta:

        st.warning(
            "ALERTA: La reclamación requiere revisión humana."
        )

    else:

        st.success(
            "La reclamación no supera el umbral de alerta."
        )

    st.write(
        "Clasificación:",
        resultado["clasificacion"]
    )

    st.info(
        "El resultado es orientativo. "
        "Sentinel no autoriza ni rechaza reclamaciones."
    )

    # Mostrar respuesta completa para evidencia técnica
    with st.expander("Ver respuesta JSON de FastAPI"):

        st.json(resultado)