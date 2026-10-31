
# Sentinel — Plan de pruebas y evidencias técnicas

## 1. Objetivo

Documentar las pruebas funcionales y de integración realizadas durante el desarrollo del proyecto educativo Sentinel.

Las pruebas tienen como finalidad verificar el funcionamiento del modelo de Machine Learning, la API REST, la interfaz web y los contenedores Docker.

## 2. Entorno de pruebas

| Componente | Tecnología |
|---|---|
| Sistema operativo | Windows |
| Entorno de desarrollo | Visual Studio Code |
| Lenguaje | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Modelo ML | Random Forest Optimizado |
| Pruebas automatizadas | Pytest |
| Contenedores | Docker 29.0.1 |
| Orquestación | Docker Compose v2.40.3 |
| Entorno de entrenamiento | Google Colab |

## 3. Pruebas del modelo de Machine Learning

El modelo se entrenó utilizando el dataset público Vehicle Insurance Claim Fraud Detection de Kaggle.

**Variable objetivo:** `FraudFound_P`.

**Modelo seleccionado:** Random Forest Optimizado.

**Umbral de alerta:** 0.19.

### Resultados de validación

| Métrica | Resultado | Meta | Cumplimiento |
|---|---:|---:|---|
| Precision | 29.59% | > 60% | No cumple |
| Recall | 31.35% | > 85% | No cumple |
| FPR | 4.76% | < 5% | Cumple |
| F1-Score | 30.45% | Sin meta definida | Informativo |

Los resultados indican que el modelo es funcional como prototipo educativo, pero no cumple todos los criterios técnicos necesarios para su utilización operativa.

Los experimentos de entrenamiento y optimización se registraron mediante MLflow.

## 4. Pruebas automatizadas del backend

Se utilizó Pytest para verificar el funcionamiento de la API
FastAPI, incluyendo validación de solicitudes, casos especiales,
consistencia de resultados y reglas de clasificación.

### Comando de ejecución

```bash
python -m pytest tests/ -v
```

### Resultados

| ID | Prueba | Resultado |
|---|---|---|
| P01 | GET /health | Aprobada |
| P02 | GET /features | Aprobada |
| P03 | POST /predict válido | Aprobada |
| P04 | Variables faltantes | Aprobada |
| P05 | Solicitud sin datos | Aprobada |
| P06 | Tipo de dato no permitido (lista) | Aprobada |
| P07 | Variable adicional | Aprobada |
| P08 | Categoría desconocida | Aprobada |
| P09 | Consistencia de predicciones | Aprobada |
| P10 | Consistencia del umbral | Aprobada |
| P11 | Probabilidad dentro del rango [0,1] | Aprobada |
| P12 | Revisión humana obligatoria | Aprobada |

**Resultado general: 12 pruebas aprobadas.**

### Análisis de resultados

Las pruebas confirman que:

- La API responde correctamente a las solicitudes de salud.
- El modelo dispone de las 32 variables requeridas.
- Se pueden generar predicciones a partir de reclamaciones válidas.
- Las solicitudes incompletas son rechazadas.
- Los tipos incompatibles con el esquema son rechazados.
- Las variables adicionales no impiden procesar la reclamación.
- Las categorías desconocidas reciben una respuesta controlada.
- Las predicciones repetidas producen resultados consistentes.
- La clasificación de alerta corresponde al umbral configurado.
- Las probabilidades devueltas se encuentran entre 0 y 1.
- El sistema conserva la indicación de revisión humana.

### Limitaciones

La prueba de categoría desconocida admite una respuesta HTTP 200
o 422; por tanto, no demuestra que la categoría sea rechazada.

La prueba de tipo incorrecto utiliza una lista como valor inválido.
No verifica todos los errores posibles de tipo.

Todavía no se han implementado pruebas completas de rangos de
negocio, carga, concurrencia o seguridad.

### Evidencias

- `docs/evidencias/pytest_12_pruebas.png`
- `docs/evidencias/pytest_resultados.txt`

## 5. Pruebas manuales de FastAPI

Se utilizó Swagger UI para comprobar los endpoints.

**Dirección:** http://127.0.0.1:8000/docs

### GET /health

Resultado: HTTP 200.

Se confirmó que la API estaba disponible y que el modelo se encontraba cargado.

### GET /features

Resultado: HTTP 200.

Se confirmó que el backend devolvía las 32 variables requeridas por el modelo.

### POST /predict

Resultado: HTTP 200.

Se utilizó una reclamación de ejemplo para verificar que el modelo podía generar una puntuación de fraude y devolver una clasificación.

## 6. Pruebas de integración con Streamlit

**Dirección:** http://localhost:8501

Se verificó que:

- La interfaz web se cargara correctamente.
- El formulario mostrara las 32 variables.
- Streamlit estableciera comunicación con FastAPI.
- El usuario pudiera enviar una reclamación.
- El resultado de la predicción se mostrara en pantalla.

La comunicación se realizó mediante solicitudes HTTP y respuestas JSON.

## 7. Pruebas de Docker

### 7.1 Verificación de Docker Engine

Se ejecutó:

```bash
docker run --rm hello-world
```

**Resultado:** `Hello from Docker!`

La prueba confirmó que Docker podía descargar imágenes y ejecutar contenedores.

### 7.2 Construcción de imagen backend

Comando:

```bash
docker build -t sentinel-backend:v1 ./backend
```

**Resultado:** imagen construida correctamente.

### 7.3 Construcción de imagen frontend

Comando:

```bash
docker build -t sentinel-frontend:v1 -f frontend/Dockerfile .
```

**Resultado:** imagen construida correctamente.

### 7.4 Ejecución del backend en Docker

Se ejecutó el contenedor del backend y se verificaron:

- GET /health: HTTP 200.
- POST /predict: HTTP 200.

Esto confirmó que el modelo podía cargarse y generar predicciones dentro del contenedor.

## 8. Pruebas de Docker Compose

### Inicio de servicios

```bash
docker compose up --build -d
```

### Verificación

```bash
docker compose ps
```

Se confirmó que los servicios backend y frontend estaban activos.

El backend presentó el estado `Up (healthy)`.

### Integración

Se verificó el acceso a:

- FastAPI: http://127.0.0.1:8000/docs
- Streamlit: http://localhost:8501

Ambas aplicaciones funcionaron desde Docker Compose.

## 9. Prueba de reinicio

Se detuvieron los contenedores mediante:

```bash
docker compose down
```

Posteriormente se iniciaron nuevamente:

```bash
docker compose up -d
```

Se verificó su estado:

```bash
docker compose ps
```

### Resultado

- Backend: Up (healthy).
- Frontend: Up.
- Formulario Streamlit disponible.
- Predicción funcional después del reinicio.

**Conclusión:** Sentinel puede detenerse y reiniciarse localmente sin volver a entrenar el modelo.

## 10. Evidencias

Las capturas de pantalla se almacenan en `docs/evidencias/`.

| Archivo | Descripción |
|---|---|
| `docker_backend_build.png` | Construcción de la imagen backend |
| `docker_backend_running.png` | Ejecución del backend en Docker |
| `docker_backend_predict.png` | Predicción mediante Swagger |
| `docker_frontend_build.png` | Construcción de la imagen frontend |
| `docker_compose_ps.png` | Estado de los contenedores |
| `docker_compose_backend.png` | Swagger desde Docker Compose |
| `docker_compose_frontend.png` | Streamlit desde Docker Compose |
| `docker_compose_prediccion.png` | Resultado de predicción |
| `docker_compose_reinicio.png` | Estado después del reinicio |

Los nombres anteriores deben coincidir con los archivos efectivamente guardados en la carpeta de evidencias.

## 11. Limitaciones de las pruebas

Las pruebas realizadas verifican el funcionamiento básico del prototipo.

No constituyen una validación de producción.

No se realizaron pruebas exhaustivas de carga, concurrencia, penetración, seguridad, resiliencia o recuperación ante desastres.

La evaluación del modelo corresponde a un dataset público y no demuestra su desempeño en una operación aseguradora real.

## 12. Conclusión

Las pruebas realizadas demuestran el funcionamiento técnico de Sentinel en un entorno local.

Se verificaron satisfactoriamente la API, la interfaz web, la integración entre componentes, la construcción de imágenes Docker y el reinicio de la aplicación mediante Docker Compose.

El modelo de Machine Learning conserva limitaciones predictivas que deberán resolverse antes de cualquier aplicación operativa real.
