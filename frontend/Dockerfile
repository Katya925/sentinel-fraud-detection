# ============================================================
# PROYECTO SENTINEL
# FASE V - CONTENEDOR FRONTEND STREAMLIT
# ============================================================

# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias del frontend
COPY frontend/requirements.txt .

# Instalar bibliotecas
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación Streamlit
COPY frontend/app.py ./frontend/app.py

# Copiar reclamación de ejemplo
COPY tests/ejemplo_reclamacion.json ./tests/ejemplo_reclamacion.json

# Puerto de Streamlit
EXPOSE 8501

# Ejecutar la aplicación
CMD ["streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501"]