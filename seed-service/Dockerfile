# syntax=docker/dockerfile:1
ARG COWLY_VERSION=0.1.0

FROM python:3.11-slim
ARG COWLY_VERSION=0.1.0

LABEL org.opencontainers.image.title="cowly-seed-service" \
      org.opencontainers.image.version="${COWLY_VERSION}" \
      org.opencontainers.image.description="One-shot demo data seeder for Cowly"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY seed.py .

CMD ["python", "seed.py"]
