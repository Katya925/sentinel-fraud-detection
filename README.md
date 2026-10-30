
# Sentinel — Detección de fraude en reclamaciones de seguros

## 1. Descripción del proyecto

Sentinel es un prototipo educativo de Machine Learning diseñado para identificar posibles reclamaciones fraudulentas en seguros de automóviles.

La solución utiliza un modelo Random Forest entrenado con un dataset público de Kaggle. Mediante una aplicación web, permite introducir información de una reclamación y obtener una puntuación estimada de riesgo de fraude.

Sentinel utiliza un enfoque **Human-in-the-Loop**: las alertas requieren revisión humana y no generan rechazos automáticos.

**Importante:** el modelo es experimental y no está aprobado para producción.

## 2. Objetivo

Desarrollar una solución técnica funcional y reproducible que integre:

- Modelo de Machine Learning en Python.
- API REST desarrollada con FastAPI.
- Interfaz web desarrollada con Streamlit.
- Contenedores Docker.
- Orquestación local mediante Docker Compose.
- Pruebas automatizadas y evidencias técnicas.
- Documentación de un posible despliegue en la nube, sin realizarlo.

## 3. Dataset

**Nombre:** Vehicle Insurance Claim Fraud Detection

**Fuente:** [Kaggle — Vehicle Insurance Claim Fraud Detection](https://www.kaggle.com/datasets/shivamb/vehicle-claim-fraud-detection)

**Variable objetivo:** `FraudFound_P`

- `0`: reclamación sin fraude identificado.
- `1`: reclamación fraudulenta.

El dataset se descarga durante el entrenamiento mediante `kagglehub.dataset_download()`.

## 4. Modelo de Machine Learning

**Modelo seleccionado:** Random Forest Optimizado.

**Umbral de alerta:** 0.19.

### Métricas de validación

| Métrica | Resultado |
|---|---:|
| Precision | 29.59% |
| Recall | 31.35% |
| F1-Score | 30.45% |
| False Positive Rate | 4.76% |

El modelo cumple la restricción de falsos positivos en validación, pero no alcanza las metas de precision y recall establecidas en el Business Case.

Los experimentos se registraron mediante MLflow.

## 5. Arquitectura

La solución utiliza tres componentes principales:

**Frontend — Streamlit:** permite capturar datos y visualizar resultados.

**Backend — FastAPI:** recibe solicitudes HTTP, valida las variables y ejecuta el modelo.

**Modelo ML — Random Forest:** procesa las 32 variables de entrada y genera una puntuación estimada de fraude.

Frontend y backend se ejecutan en contenedores independientes, conectados mediante Docker Compose.

## 6. Tecnologías utilizadas

- Python
- Pandas y NumPy
- Scikit-learn
- Imbalanced-learn
- MLflow
- FastAPI
- Streamlit
- Pytest
- Docker
- Docker Compose
- Git y GitHub

## 7. Requisitos previos

Para ejecutar Sentinel localmente se requiere:

- Docker Desktop instalado y funcionando.
- Docker Compose disponible.
- Acceso a los archivos del proyecto.
- Puertos 8000 y 8501 disponibles.

No es necesario volver a entrenar el modelo para ejecutar la aplicación.

## 8. Ejecución local con Docker Compose

Desde la carpeta principal del proyecto:

```bash
docker compose up --build -d
```

Verificar el estado:

```bash
docker compose ps
```

Acceder a las aplicaciones:

**Frontend:** http://localhost:8501

**Backend:** http://127.0.0.1:8000/docs

Para detener los contenedores:

```bash
docker compose down
```

Para volver a iniciarlos:

```bash
docker compose up -d
```

## 9. API REST

La API dispone de tres endpoints:

| Método | Endpoint | Función |
|---|---|---|
| GET | `/health` | Comprobar el estado del servicio |
| GET | `/features` | Consultar las variables requeridas |
| POST | `/predict` | Obtener la predicción de fraude |

La respuesta de `/predict` contiene la puntuación estimada, el umbral, la clasificación y la indicación de revisión humana.

## 10. Pruebas realizadas

Se ejecutaron cuatro pruebas automatizadas mediante Pytest, todas satisfactorias.

También se realizaron pruebas manuales de:

- Carga del modelo en FastAPI.
- Predicción mediante Swagger.
- Integración entre Streamlit y FastAPI.
- Construcción de imágenes Docker.
- Ejecución mediante Docker Compose.
- Reinicio de contenedores.
- Predicción después del reinicio.

Las capturas correspondientes se conservan en `docs/evidencias/`.

## 11. Limitaciones

Sentinel es un prototipo educativo.

El modelo no cumple todos los KPI del Business Case y requiere mejoras antes de considerar cualquier utilización operativa.

La puntuación estimada no constituye una determinación definitiva de fraude.

La aplicación no automatiza rechazos, autorizaciones ni pagos de reclamaciones.

## 12. Despliegue en la nube

El proyecto no contempla un despliegue real en infraestructura cloud.

El procedimiento de despliegue se describirá en `docs/manual_despliegue.md` como referencia técnica para una posible implementación futura.

## 13. Alcance académico

El proyecto demuestra la integración funcional de Machine Learning, API REST, interfaz web y contenedores Docker en un entorno local.

Su propósito es educativo y no representa una solución productiva de una compañía aseguradora.
