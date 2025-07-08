# Multi-stage Dockerfile for Sound Realty API

# --- Base image ---
FROM python:3.9-slim as base
WORKDIR /app
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --- Development image ---
FROM base as dev
COPY src/ .
COPY model/ ./model/
COPY data/ ./data/
CMD ["python", "app_development.py"]

# --- Production image ---
FROM base as prod
COPY src/ .
COPY model/ ./model/
COPY data/ ./data/
CMD ["python", "app_production.py"]
