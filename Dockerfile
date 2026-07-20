FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source, static pages, and assets
COPY backend /app/backend
COPY crawled_data /app/crawled_data
COPY frontend /app/frontend

WORKDIR /app/backend

EXPOSE 8001

# Run database seed on startup then start Uvicorn server on Render's $PORT
CMD ["sh", "-c", "until python seed_data.py; do echo 'Waiting for DB to be ready...'; sleep 2; done && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 2"]

