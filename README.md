# Cowly

Smart livestock management platform built as a **microservices** backend. Cowly helps farms track cattle, manage smart collar inventory, ingest telemetry, and receive alerts when something needs attention.

> **Status:** Active development — APIs and architecture may evolve.

---

## Table of contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Services](#services)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick start (Docker)](#quick-start-docker)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [API usage](#api-usage)
- [Project structure](#project-structure)
- [Running tests](#running-tests)
- [Local development (without Docker)](#local-development-without-docker)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

Cowly models a modern farm operations stack:

1. **Farmers** register and sign in (JWT auth).
2. **Herd records** store canonical cow data (ear tags, breed, weight, etc.).
3. **Collar registry** tracks physical collar inventory and assignments.
4. **Collar simulator** mimics BLE scan → LED identify → cow pairing (for local dev without hardware).
5. **Telemetry** ingests GPS, activity, and sensor readings from collars.
6. **Alerts** fire on geofence, battery, inactivity, or temperature events.
7. **Notifications** deliver push/email/SMS-style messages to farmers (stub delivery in dev).

All client traffic should go through the **API Gateway** (`:8000`), which enforces authentication and proxies to backend services.

---

## Architecture

```mermaid
flowchart TB
    Client[Web / Mobile Client]

    subgraph Gateway
        GW[API Gateway :8000]
    end

    subgraph Services
        AUTH[Auth :8102]
        HERD[Herd :8103]
        REG[Collar Registry :8104]
        SIM[Collar Simulator :8101]
        TEL[Telemetry :8105]
        ALT[Alerts :8106]
        NOT[Notifications :8107]
    end

    subgraph Data
        PG[(PostgreSQL)]
        RD[(Redis)]
    end

    Client --> GW
    GW --> AUTH
    GW --> HERD
    GW --> REG
    GW --> SIM
    GW --> TEL
    GW --> ALT
    GW --> NOT
    REG --> SIM
    ALT --> NOT

    AUTH --> PG
    HERD --> PG
    REG --> PG
    TEL --> PG
    ALT --> PG
    NOT --> PG
```

Each data-owning service uses its **own PostgreSQL database** on a shared Postgres instance (logical separation, one DB per bounded context).

---

## Services

| Service | Port | Database | Description |
|---------|------|----------|-------------|
| **api-gateway** | 8000 | — | Single entry point, JWT enforcement, request proxying |
| **collar-simulator** | 8101 | — | Simulates smart collars (scan, LED blink, assign) |
| **auth-service** | 8102 | `cowly_auth` | Register, login, JWT issue & verify |
| **herd-service** | 8103 | `cowly_herd` | Cow / herd CRUD |
| **collar-registry** | 8104 | `cowly_collar` | Collar inventory & pairing state |
| **telemetry-service** | 8105 | `cowly_telemetry` | GPS & sensor reading ingest |
| **alert-service** | 8106 | `cowly_alerts` | Operational & health alerts |
| **notification-service** | 8107 | `cowly_notifications` | Farmer notifications |
| **postgres** | 5433→5432 | — | Shared Postgres host (per-service DBs) |
| **redis** | 6380→6379 | — | Reserved for future caching / queues |

**Use the gateway in development:** `http://localhost:8000`  
Individual service ports are exposed for debugging; in production, only the gateway should be public.

Interactive API docs (per service): `http://localhost:<port>/docs`  
Gateway overview: `http://localhost:8000/`

---

## Tech stack

- **Python 3.11** · **FastAPI** · **Uvicorn**
- **SQLModel** + **PostgreSQL** (per-service databases)
- **JWT** (python-jose) · **bcrypt** password hashing
- **Docker** & **Docker Compose**
- **pytest** + **httpx** for tests

---

## Prerequisites

Install on your machine:

| Tool | Version | Notes |
|------|---------|--------|
| [Docker](https://docs.docker.com/get-docker/) | 20+ | Required for recommended setup |
| [Docker Compose](https://docs.docker.com/compose/install/) | v2+ | Usually bundled with Docker Desktop |
| [Git](https://git-scm.com/) | any | Clone the repository |

Optional (local dev without Docker):

- Python **3.11** only if you run services outside Docker (tests use Docker — see [Running tests](#running-tests))
- PostgreSQL client tools (optional)

---

## Quick start (Docker)

### One-command setup (recommended)

```bash
git clone <your-repo-url> cowly
cd cowly
./scripts/setup.sh --seed
```

This creates `.env` from `.env.example`, builds images, waits for health, and loads demo data (`demo@cowly.local` / `demo-password-1`).

Equivalent via Make:

```bash
make setup-seed
```

### Manual steps

```bash
cp .env.example .env    # customize JWT secret and ports if needed
make up                 # or: docker compose up --build -d
make health
make seed               # optional demo data
```

First startup creates Postgres databases via `docker/postgres/init-databases.sql` and each service runs schema migrations (`create_all`) on boot.

### Verify

```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
```

### Open API docs

| Service | Swagger UI |
|---------|------------|
| Gateway | [http://localhost:8000](http://localhost:8000) |
| Auth | [http://localhost:8102/docs](http://localhost:8102/docs) |
| Herd | [http://localhost:8103/docs](http://localhost:8103/docs) |

### Run from pre-built images (no source build)

After publishing images with `./scripts/build-and-push.sh` (set `COWLY_IMAGE_REGISTRY`):

```bash
cp .env.example .env
docker compose -f docker-compose.pull.yml pull
docker compose -f docker-compose.pull.yml up -d
```

Or: `make pull && make up-pull`

### Common Make targets

| Command | Description |
|---------|-------------|
| `make up` / `make down` | Start / stop stack (data preserved) |
| `make logs` | Follow logs |
| `make seed` | Load demo herd, collar, telemetry |
| `make dev` | Dev overrides (debug logging) |
| `make watch` | Live-sync code into containers |
| `make backup` | Dump all Postgres DBs to `backups/` |
| `make reset` | Wipe database volume (with confirmation) |
| `make build-images` | Build tagged images locally |
| `make test` | Unit tests in Docker (Python 3.11) |
| `make test-service SVC=herd-service` | Test one service in Docker |
| `make test-integration` | Unit + E2E tests (starts stack if needed) |

### Stop

```bash
docker compose down
```

### Reset database (fresh Postgres)

If databases were created before the init script existed:

```bash
docker compose down
docker volume rm cowly_postgres_data
docker compose up --build
```

---

## Configuration

Key environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `COWLY_VERSION` | Release tag for images (defaults to `VERSION` file) |
| `COWLY_IMAGE_REGISTRY` | Docker image prefix (default `cowly`, e.g. `ghcr.io/you/cowly`) |
| `COWLY_AUTH_JWT_SECRET` | Shared secret for JWT signing (all services + gateway) |
| `COWLY_GATEWAY_CORS_ORIGINS` | Comma-separated origins or `*` |
| `COWLY_LOG_LEVEL` | `info` or `debug` for all services |
| `COWLY_*_PORT` | Host port mappings (gateway, services, Postgres, Redis) |
| `COWLY_COLLAR_SIM_HERD_SIZE` | Number of simulated collars seeded on startup |
| `COWLY_INTERNAL_API_KEY` | Service-to-service key (alert → notification) |
| `COWLY_SEED_*` | Demo user credentials for `make seed` |

Inside Docker, each service receives its own `DATABASE_URL` pointing at `postgres:5432/<db_name>`.  
On the host machine, Postgres is reachable at `localhost:5433`.

---

## Authentication

Protected routes require a Bearer token from login.

**Public (no token):**

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /health`
- `GET /version`

**Protected:** all other `/api/v1/*` routes through the gateway (including `POST /api/v1/auth/logout`).

Login returns `access_token` and `refresh_token`. JWT claims include `farm_id` for tenant isolation.

### Example flow

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "password123",
    "farm_name": "Green Pastures"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "password123"
  }'

# Save access_token from response, then:
export TOKEN="<access_token>"

# Authenticated request
curl http://localhost:8000/api/v1/herd \
  -H "Authorization: Bearer $TOKEN"
```

Without a token:

```bash
curl http://localhost:8000/api/v1/herd
# → 401 {"detail":"Not authenticated"}
```

---

## API usage

Gateway route prefixes:

| Prefix | Backend |
|--------|---------|
| `/api/v1/auth/*` | auth-service |
| `/api/v1/herd/*` | herd-service (cows) |
| `/api/v1/collars/*` | collar-registry |
| `/api/v1/simulator/*` | collar-simulator (via registry proxy) |
| `/api/v1/telemetry/*` | telemetry-service |
| `/api/v1/alerts/*` | alert-service |
| `/api/v1/notifications/*` | notification-service |

### Example: create a cow and register a collar

```bash
# Create cow
curl -X POST http://localhost:8000/api/v1/herd \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Bessie","ear_tag":"TAG-001","breed":"Holstein"}'

# Register collar
curl -X POST http://localhost:8000/api/v1/collars \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mac_address":"AA:BB:CC:DD:EE:01","firmware_version":"1.0.0"}'

# Scan nearby collars (simulator)
curl http://localhost:8000/api/v1/simulator/collars/scan \
  -H "Authorization: Bearer $TOKEN"
```

---

## Project structure

```
cowly/
├── api-gateway/           # Entry point, auth middleware, proxy
├── auth-service/
├── herd-service/
├── collar-registry/
├── collar-simulator/      # In-memory hardware simulation
├── telemetry-service/
├── alert-service/
├── notification-service/
├── integration/           # End-to-end tests (gateway)
├── docker/
│   └── postgres/          # DB init scripts
├── scripts/
│   ├── run_all_tests.sh      # All unit tests in Docker (Python 3.11)
│   └── run_service_tests.sh  # Single-service tests in Docker
├── docker-compose.yml
├── docker-compose.test.yml # Integration test runner
├── docker/test-runner/     # Python 3.11 E2E test image
├── pytest.ini
├── .env.example
└── README.md
```

### Code layout (per service)

Each domain module follows the same pattern:

```
app/
├── main.py
├── config.py
├── database.py
└── <domain>/
    ├── models.py      # SQLModel tables (database)
    ├── schemas.py     # Pydantic request/response DTOs
    ├── service.py     # Business logic
    └── routes.py      # HTTP handlers
```

---

## Running tests

Tests run **inside Docker** using **Python 3.11** (same as production images). You do not need Python installed on the host.

**Requirements:** Docker + Docker Compose v2, and permission to run `docker` (e.g. your user in the `docker` group).

**Before you push (recommended):**

```bash
make test                 # unit tests only (~2 min)
make test-integration     # unit + E2E; starts stack if needed (~5–10 min)
```

### All unit tests

```bash
make test
# or
./scripts/run_all_tests.sh
```

This builds each service image and runs `pytest` in a one-off container with SQLite and `COWLY_SKIP_MIGRATIONS=1`. Tests set `PYTHONPATH=.` so the `app` package resolves inside each service image.

### One service

```bash
make test-service SVC=auth-service
# or
./scripts/run_service_tests.sh herd-service
```

### Integration tests (full stack)

Runs E2E tests from a **Python 3.11 test container** on the Compose network (`http://api-gateway:8000`). If the stack is not up, `make test-integration` starts it and waits for the gateway to be healthy.

```bash
make test-integration
# or
RUN_INTEGRATION=1 ./scripts/run_all_tests.sh
```

To require a pre-started stack (fail instead of auto-start): `COWLY_INTEGRATION_NO_START=1 make test-integration`

Optional env vars for integration runs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `COWLY_INTEGRATION_NO_START` | `0` | Set to `1` to skip auto `docker compose up` |
| `COWLY_INTEGRATION_NO_RESET` | `0` | Set to `1` to disable auto `docker compose down -v` retry when the stack stays unhealthy |
| `COWLY_INTEGRATION_WAIT_ATTEMPTS` | `90` | Health poll attempts (2s apart) when waiting for gateway |

Integration tests cover register → login → herd → collars → telemetry → alerts → notifications.

### Test layout

| Path | Purpose |
|------|---------|
| `<service>/tests/` | Unit tests (run in that service’s Docker image) |
| `<service>/requirements-dev.txt` | pytest + httpx (+ respx where needed) |
| `integration/` | E2E via gateway (`docker/test-runner`) |
| `docker-compose.test.yml` | Integration test service definition |

---

## Local development (without Docker)

For running **services** locally (not tests), use Python 3.11 and a venv:

1. Start Postgres (or use `docker compose up postgres redis -d` only).
2. Ensure databases exist (`docker/postgres/init-databases.sql`).
3. In each service directory:

```bash
cd auth-service
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export COWLY_AUTH_DATABASE_URL=postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_auth
export COWLY_AUTH_REDIS_URL=redis://localhost:6380/0
python run.py
```

Repeat for other services with their ports and `DATABASE_URL` values from `docker-compose.yml`.

To run **tests**, use Docker instead: `make test`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `address already in use` on port 5432 | Host Postgres conflicts; Cowly maps Postgres to **5433** |
| Services connect to `localhost:5433` inside Docker | Rebuild after `docker-compose.yml` fix; URLs must use host `postgres:5432` in containers |
| `database "cowly_auth" does not exist` | Reset volume: `docker volume rm cowly_postgres_data` and `docker compose up --build` |
| `401 Not authenticated` | Login first; pass `Authorization: Bearer <token>` on protected routes |
| Auth register returns 500 (bcrypt) | Rebuild auth-service image after dependency updates |
| `permission denied` on `docker.sock` | `sudo usermod -aG docker $USER` then **reboot** (or run `newgrp docker`). Check: `groups \| grep docker` must show `docker`. `make test` auto-uses `sg docker` if group exists but shell is stale. |
| Tests fail locally on Python 3.8 | Use `make test` — tests run in Docker with Python 3.11 |
| `ModuleNotFoundError: No module named 'app'` | Run via `make test` / `scripts/run_all_tests.sh` (sets `PYTHONPATH=.` in containers) |
| Integration tests fail on gateway | `make test-integration` auto-starts the stack and retries once with a fresh DB volume; manual reset: `docker compose down -v && docker compose up -d --wait` |

---

## Features (recent)

- **Multi-tenancy:** Each farmer gets a `farm_id`; all herd, collar, telemetry, alert, and notification data is scoped to that farm.
- **Auto-alerts:** Telemetry ingest evaluates battery, temperature, activity, and geofence rules; alerts notify via email (SMTP when enabled).
- **Geofences:** Circular zones per farm (`POST /api/v1/geofences`); exit triggers `geofence_exit` alerts.
- **Auth:** Access + refresh tokens; `POST /api/v1/auth/refresh` and `POST /api/v1/auth/logout` with Redis revocation.
- **Migrations:** Alembic per database service (`alembic upgrade head` on startup).
- **Pinned deps:** `requirements.lock` per service — regenerate with `./scripts/compile-requirements.sh`.

## Roadmap

- [ ] Mobile / web client application
- [ ] Real IoT ingestion (MQTT) replacing simulator
- [ ] Redis-backed async notification queue (worker)
- [ ] Push / SMS providers (FCM, Twilio)
- [ ] Kubernetes / production deployment manifests

---

## License

<!-- Add your license here, e.g. MIT, Apache-2.0 -->

*License TBD.*
