FROM python:3.11-slim


ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m appuser


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .
RUN mkdir -p static && chown -R appuser:appuser /app


USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]