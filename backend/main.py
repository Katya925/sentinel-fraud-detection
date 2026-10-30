# ============================================================
# PROYECTO SENTINEL
# FASE II - BACKEND CON FASTAPI
# Detección de fraude en reclamaciones de seguros
# ============================================================

import json
import joblib
import pandas as pd

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "sentinel_pipeline.joblib"
METADATA_PATH = BASE_DIR / "sentinel_metadata.json"


# ============================================================
# 2. CARGA DEL MODELO Y METADATOS
# ============================================================

modelo = None
metadata = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global modelo, metadata

    # Cargar metadatos
    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as archivo:

        metadata = json.load(archivo)

    # Cargar modelo entrenado
    # Solo cargar archivos generados por fuentes confiables
    modelo = joblib.load(MODEL_PATH)

    print("Modelo Sentinel cargado correctamente.")

    yield


# ============================================================
# 3. CREACIÓN DE LA API
# ============================================================

app = FastAPI(
    title="Sentinel API",
    description=(
        "API educativa para detección de posibles "
        "fraudes en reclamaciones de seguros."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# 4. MODELO DE DATOS DE ENTRADA
# ============================================================

class Reclamacion(BaseModel):

    datos: dict[str, str | int | float | bool] = Field(
        description="Variables de la reclamación"
    )


# ============================================================
# 5. ENDPOINT DE SALUD
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "modelo_cargado": modelo is not None,
        "proyecto": "Sentinel"
    }


# ============================================================
# 6. CONSULTAR VARIABLES DEL MODELO
# ============================================================

@app.get("/features")
def features():

    return {
        "modelo": metadata["modelo"],
        "variables": metadata["variables_entrada"],
        "total_variables": len(
            metadata["variables_entrada"]
        )
    }


# ============================================================
# 7. ENDPOINT DE PREDICCIÓN
# ============================================================

@app.post("/predict")
def predict(reclamacion: Reclamacion):

    try:

        # Obtener las variables requeridas
        variables = metadata["variables_entrada"]

        # Verificar que no falten variables
        faltantes = [
            variable
            for variable in variables
            if variable not in reclamacion.datos
        ]

        if faltantes:

            raise HTTPException(
                status_code=422,
                detail={
                    "mensaje": "Faltan variables requeridas",
                    "variables_faltantes": faltantes
                }
            )

        # Construir DataFrame con el orden correcto
        datos = pd.DataFrame(
            [reclamacion.datos]
        )

        datos = datos[variables]

        # Obtener probabilidad de fraude
        probabilidad = float(
            modelo.predict_proba(datos)[0, 1]
        )

        # Recuperar umbral
        umbral = float(
            metadata["umbral_alerta"]
        )

        # Determinar si corresponde generar alerta
        alerta = probabilidad >= umbral

        # Devolver resultado
        return {
            "probabilidad_fraude": round(
                probabilidad, 4
            ),
            "umbral_alerta": umbral,
            "alerta": bool(alerta),
            "clasificacion": (
                "Revision requerida"
                if alerta
                else "Sin alerta de alto riesgo"
            ),
            "requiere_revision_humana": True,
            "apto_para_produccion": False
        }

    except HTTPException:
        raise

    except (ValueError, TypeError, KeyError) as error:

        raise HTTPException(
            status_code=422,
            detail="Los datos de la reclamación no son válidos."
        ) from error