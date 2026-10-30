# ============================================================
# PROYECTO SENTINEL
# FASE V - CONTENEDOR BACKEND FASTAPI
# ============================================================

# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y modelo entrenado
COPY main.py .
COPY sentinel_pipeline.joblib .
COPY sentinel_metadata.json .

# Puerto utilizado por FastAPI
EXPOSE 8000

# Iniciar la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]