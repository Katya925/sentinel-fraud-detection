
# Sentinel — Manual técnico de despliegue

## 1. Objetivo

Documentar el procedimiento para construir, ejecutar y verificar la aplicación Sentinel mediante contenedores Docker.

El manual incluye:

- Requisitos técnicos.
- Construcción de imágenes.
- Ejecución local mediante Docker Compose.
- Pruebas de funcionamiento.
- Solución de problemas frecuentes.
- Estrategia propuesta para un eventual despliegue en la nube.

**Alcance:** el despliegue local fue ejecutado y validado. El despliegue en la nube es únicamente una propuesta documental y no fue realizado.

## 2. Arquitectura

Sentinel utiliza dos servicios:

| Servicio | Tecnología | Puerto |
|---|---|---|
| Backend | FastAPI + Random Forest | 8000 |
| Frontend | Streamlit | 8501 |

El frontend se comunica con el backend mediante HTTP y JSON.

Docker Compose administra ambos servicios y proporciona una red interna para su comunicación.

## 3. Requisitos previos

Para ejecutar Sentinel localmente se necesita:

- Windows con Docker Desktop y WSL 2.
- Docker Engine funcionando.
- Docker Compose disponible.
- Código fuente del proyecto.
- Modelo `sentinel_pipeline.joblib`.
- Metadatos `sentinel_metadata.json`.
- Puertos 8000 y 8501 disponibles.

Versiones utilizadas durante el desarrollo:

| Herramienta | Versión |
|---|---|
| Docker | 29.0.1 |
| Docker Compose | 2.40.3 |
| Scikit-learn | 1.6.1 |
| Imbalanced-learn | 0.14.2 |
| NumPy | 2.1.3 |
| Pandas | 2.2.3 |
| Joblib | 1.6.0 |

Las versiones de las bibliotecas corresponden al entorno utilizado para entrenar el modelo en Google Colab.

## 4. Estructura del proyecto

```text
Sentinel/
├── backend/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── sentinel_pipeline.joblib
│   └── sentinel_metadata.json
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── tests/
│   ├── test_api.py
│   └── ejemplo_reclamacion.json
├── docs/
│   ├── arquitectura.md
│   ├── pruebas.md
│   ├── manual_despliegue.md
│   └── evidencias/
├── compose.yaml
└── README.md
```

## 5. Verificación de Docker

Abrir Docker Desktop y comprobar que Docker Engine esté funcionando.

Desde una terminal, ejecutar:

```bash
docker --version
docker compose version
docker info
```

Para comprobar la ejecución de contenedores:

```bash
docker run --rm hello-world
```

El resultado esperado incluye:

```text
Hello from Docker!
```

## 6. Construcción de imágenes

### Backend

Desde la carpeta principal Sentinel:

```bash
docker build -t sentinel-backend:v1 ./backend
```

### Frontend

```bash
docker build -t sentinel-frontend:v1 -f frontend/Dockerfile .
```

### Verificar imágenes

```bash
docker images
```

Deben aparecer:

- `sentinel-backend:v1`
- `sentinel-frontend:v1`

## 7. Ejecución local con Docker Compose

### Validar configuración

```bash
docker compose config
```

### Construir e iniciar servicios

```bash
docker compose up --build -d
```

### Verificar contenedores

```bash
docker compose ps
```

Estados esperados:

- Backend: `Up (healthy)`.
- Frontend: `Up`.

## 8. Acceso a Sentinel

Una vez iniciados los contenedores:

**Frontend:**

http://localhost:8501

**Backend:**

http://127.0.0.1:8000/docs

### Verificación funcional

1. Abrir Streamlit.
2. Comprobar la conexión con FastAPI.
3. Revisar el formulario de 32 variables.
4. Enviar una reclamación de ejemplo.
5. Verificar la puntuación estimada y la clasificación.
6. Confirmar que la decisión requiere revisión humana.

## 9. Gestión de contenedores

### Detener servicios

```bash
docker compose down
```

### Reiniciar servicios

```bash
docker compose up -d
```

### Consultar estado

```bash
docker compose ps
```

### Consultar registros

```bash
docker compose logs --tail=50
```

### Reconstruir imágenes

```bash
docker compose up --build -d
```

## 10. Problemas frecuentes

### Puerto 8000 ocupado

**Síntoma:**

```text
port is already allocated
```

**Acción:**

Identificar qué proceso o contenedor utiliza el puerto 8000 y detenerlo de forma controlada.

```bash
docker ps
```

### Streamlit no conecta con FastAPI

Verificar:

- Que ambos contenedores estén activos.
- Que el backend esté saludable.
- Que la variable `API_URL` tenga el valor `http://backend:8000`.
- Que la red interna de Docker Compose esté funcionando.

### Error al cargar el modelo

Verificar la compatibilidad entre las versiones utilizadas durante el entrenamiento y las instaladas en el contenedor.

El modelo fue entrenado utilizando Scikit-learn 1.6.1.

### Docker Desktop no inicia

Verificar el estado de WSL 2 y el servicio Docker Desktop.

No utilizar `Reset to factory defaults` sin evaluar previamente sus consecuencias, ya que podría eliminar recursos locales.

## 11. Estrategia propuesta de despliegue en la nube

**Esta sección es exclusivamente documental. No se realizó ningún despliegue cloud.**

### Plataforma propuesta

Google Cloud Run.

Esta plataforma permite ejecutar aplicaciones contenerizadas mediante servicios administrados.

### Arquitectura propuesta

Se plantea desplegar:

- Un servicio Cloud Run para el frontend Streamlit.
- Un servicio Cloud Run para el backend FastAPI.
- Artifact Registry para almacenar las imágenes Docker.

El frontend enviaría solicitudes al backend mediante HTTPS.

### 11.1 Preparación

1. Crear un proyecto en Google Cloud.
2. Configurar facturación y presupuestos.
3. Habilitar las API necesarias.
4. Crear un repositorio en Artifact Registry.
5. Configurar identidades y permisos mínimos.

### 11.2 Construcción y publicación de imágenes

Como procedimiento propuesto:

1. Autenticar Docker contra Artifact Registry.
2. Etiquetar las imágenes con la ubicación del registro.
3. Publicar las imágenes.
4. Verificar su disponibilidad.

Los comandos exactos deberán adaptarse al identificador del proyecto, la región y el repositorio configurados.

### 11.3 Despliegue del backend

1. Crear un servicio Cloud Run.
2. Seleccionar la imagen del backend.
3. Configurar el puerto 8000.
4. Establecer memoria y CPU suficientes para cargar el modelo.
5. Configurar una cuenta de servicio con permisos mínimos.
6. Restringir el acceso al backend mediante autenticación.
7. Comprobar el endpoint `/health`.

### 11.4 Despliegue del frontend

1. Crear un segundo servicio Cloud Run.
2. Seleccionar la imagen de Streamlit.
3. Configurar el puerto 8501.
4. Establecer `API_URL` con la dirección HTTPS del backend.
5. Configurar autenticación entre servicios.
6. Verificar la comunicación entre frontend y backend.

La configuración local `http://backend:8000` no debe trasladarse directamente a Cloud Run, porque los servicios no comparten la misma red de Docker Compose.

### 11.5 Seguridad

Para un despliegue real se requeriría:

- Autenticación de usuarios.
- Autorización por roles.
- Protección de los endpoints.
- Comunicación HTTPS.
- Gestión segura de secretos.
- Registro y monitoreo.
- Restricción de permisos.
- Protección de datos personales.

El prototipo actual no incorpora todas estas capacidades.

### 11.6 Pruebas posteriores al despliegue

En una implementación futura se deberían ejecutar:

1. Pruebas de salud.
2. Pruebas de predicción.
3. Pruebas de autenticación.
4. Pruebas de integración.
5. Pruebas de carga.
6. Pruebas de recuperación.
7. Validación de registros y monitoreo.

### 11.7 Costes y eliminación de recursos

Antes de un despliegue real se deberían estimar:

- Consumo de CPU y memoria.
- Número de solicitudes.
- Almacenamiento de imágenes.
- Tráfico de red.
- Costes de registro y monitoreo.

También se debería documentar el procedimiento para eliminar servicios, imágenes y otros recursos, evitando gastos innecesarios.

## 12. Limitaciones

Sentinel es un prototipo educativo.

El modelo no cumple todas las metas del Business Case.

El sistema no está preparado para procesar reclamaciones reales en un entorno productivo.

La arquitectura cloud propuesta no ha sido implementada ni validada.

## 13. Conclusión

Sentinel fue construido, ejecutado y validado localmente mediante Docker y Docker Compose.

La integración entre Streamlit, FastAPI y el modelo Random Forest funciona en el entorno local.

El presente manual proporciona las instrucciones para reproducir la solución y una estrategia documental para un eventual despliegue en la nube.
