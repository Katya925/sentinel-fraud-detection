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