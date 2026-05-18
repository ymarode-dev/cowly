# syntax=docker/dockerfile:1
ARG COWLY_VERSION=0.1.0
ARG BUILD_TIMESTAMP=unknown
ARG VCS_REF=unknown

FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime
ARG COWLY_VERSION=0.1.0
ARG BUILD_TIMESTAMP=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="cowly-api-gateway" \
      org.opencontainers.image.version="${COWLY_VERSION}" \
      org.opencontainers.image.source="https://github.com/cowly/cowly" \
      org.opencontainers.image.description="Cowly API Gateway"

ENV COWLY_VERSION=${COWLY_VERSION} \
    COWLY_BUILD_TIMESTAMP=${BUILD_TIMESTAMP} \
    COWLY_VCS_REF=${VCS_REF}

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
