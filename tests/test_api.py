# ============================================================
# SENTINEL - PRUEBAS AUTOMATIZADAS DE FASTAPI
# ============================================================

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app


# Directorio de pruebas
TEST_DIR = Path(__file__).resolve().parent


# Crear cliente de prueba
@pytest.fixture(scope="module")
def client():

    # Inicializar la aplicación y cargar el modelo
    with TestClient(app) as cliente:
        yield cliente


# ============================================================
# PRUEBA 1: VERIFICAR ESTADO DE LA API
# ============================================================

def test_health(client):

    respuesta = client.get("/health")

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["status"] == "ok"
    assert datos["modelo_cargado"] is True


# ============================================================
# PRUEBA 2: VERIFICAR VARIABLES DEL MODELO
# ============================================================

def test_features(client):

    respuesta = client.get("/features")

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["total_variables"] == 32

    assert "FraudFound_P" not in datos["variables"]


# ============================================================
# PRUEBA 3: PREDICCIÓN EXITOSA
# ============================================================

def test_predict(client):

    ruta = TEST_DIR / "ejemplo_reclamacion.json"

    with open(ruta, encoding="utf-8") as archivo:
        reclamacion = json.load(archivo)

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert 0 <= resultado["probabilidad_fraude"] <= 1

    assert resultado["umbral_alerta"] == 0.19

    assert resultado["alerta"] == (
        resultado["probabilidad_fraude"] >= 0.19
    )

    assert resultado["requiere_revision_humana"] is True

    assert resultado["apto_para_produccion"] is False


# ============================================================
# PRUEBA 4: RECHAZAR VARIABLES FALTANTES
# ============================================================

def test_predict_variables_faltantes(client):

    respuesta = client.post(
        "/predict",
        json={
            "datos": {
                "Age": 35
            }
        }
    )

    assert respuesta.status_code == 422

    # ============================================================
# SENTINEL - PRUEBAS ADICIONALES
# Validación de entradas, casos extremos y consistencia
# ============================================================

# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================

def obtener_reclamacion():

    ruta = TEST_DIR / "ejemplo_reclamacion.json"

    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


# ============================================================
# P05: SOLICITUD SIN EL CAMPO DATOS
# ============================================================

def test_predict_sin_datos(client):

    respuesta = client.post(
        "/predict",
        json={}
    )

    assert respuesta.status_code == 422


# ============================================================
# P06: TIPO DE DATO NO PERMITIDO
# ============================================================

def test_predict_tipo_incorrecto(client):

    reclamacion = obtener_reclamacion()

    # El esquema de entrada no admite listas
    reclamacion["datos"]["Age"] = [35, 40]

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    assert respuesta.status_code == 422


# ============================================================
# P07: VARIABLE ADICIONAL
# ============================================================

def test_predict_variable_adicional(client):

    reclamacion = obtener_reclamacion()

    reclamacion["datos"]["Variable_Desconocida"] = 123

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    # El backend actual selecciona únicamente
    # las variables esperadas por el modelo.
    assert respuesta.status_code == 200


# ============================================================
# P08: CATEGORÍA DESCONOCIDA
# ============================================================

def test_predict_categoria_desconocida(client):

    reclamacion = obtener_reclamacion()

    reclamacion["datos"]["Make"] = "MARCA_INEXISTENTE"

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    # Se espera una respuesta controlada.
    # El preprocesamiento podría aceptar
    # categorías no observadas durante entrenamiento.
    assert respuesta.status_code in [200, 422]


# ============================================================
# P09: CONSISTENCIA DE PREDICCIONES
# ============================================================

def test_predict_consistencia(client):

    reclamacion = obtener_reclamacion()

    respuesta_1 = client.post(
        "/predict",
        json=reclamacion
    )

    respuesta_2 = client.post(
        "/predict",
        json=reclamacion
    )

    assert respuesta_1.status_code == 200
    assert respuesta_2.status_code == 200

    assert respuesta_1.json() == respuesta_2.json()


# ============================================================
# P10: CONSISTENCIA DEL UMBRAL
# ============================================================

def test_predict_umbral(client):

    reclamacion = obtener_reclamacion()

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    probabilidad = resultado["probabilidad_fraude"]
    umbral = resultado["umbral_alerta"]

    assert resultado["alerta"] == (
        probabilidad >= umbral
    )


# ============================================================
# P11: PROBABILIDAD EN RANGO VÁLIDO
# ============================================================

def test_predict_probabilidad(client):

    reclamacion = obtener_reclamacion()

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    assert respuesta.status_code == 200

    probabilidad = respuesta.json()[
        "probabilidad_fraude"
    ]

    assert 0 <= probabilidad <= 1


# ============================================================
# P12: REVISIÓN HUMANA OBLIGATORIA
# ============================================================

def test_predict_revision_humana(client):

    reclamacion = obtener_reclamacion()

    respuesta = client.post(
        "/predict",
        json=reclamacion
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert resultado["requiere_revision_humana"] is True
    assert resultado["apto_para_produccion"] is Falsepyt