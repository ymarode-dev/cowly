# Cowly

Smart livestock management platform built as a **microservices** backend. Cowly helps farms track cattle, manage smart collar inventory, ingest telemetry, and receive alerts when something needs attention.

> **Status:** Active development — APIs and architecture may evolve.

---

## Table of contents

- [Overview](#overview)
- [Demo & media](#demo--media)
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

## Demo & media

Place screenshots, diagrams, and walkthrough videos here as the product grows.

### Screenshots

| | |
|---|---|
| **Dashboard** | `docs/images/dashboard.png` *(coming soon)* |
| **Herd view** | `docs/images/herd-view.png` *(coming soon)* |
| **Collar pairing flow** | `docs/images/collar-pairing.png` *(coming soon)* |
| **Alerts** | `docs/images/alerts.png` *(coming soon)* |

<!--
When ready, add images to docs/images/ and embed like:

![Cowly dashboard](docs/images/dashboard.png)
-->

### Architecture diagram (image)

`docs/images/architecture.png` *(optional high-res export of the diagram below)*

### Video walkthroughs

| Topic | Path |
|-------|------|
| Full platform tour | `docs/videos/platform-overview.mp4` *(coming soon)* |
| Docker setup | `docs/videos/local-setup.mp4` *(coming soon)* |
| Collar scan & assign demo | `docs/videos/collar-pairing-demo.mp4` *(coming soon)* |

<!--
When ready, link or embed:

https://user-images.githubusercontent.com/.../platform-overview.mp4
-->

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

- Python **3.10+** (3.11 recommended)
- PostgreSQL client tools (optional)

---

## Quick start (Docker)

### 1. Clone the repository

```bash
git clone <your-repo-url> cowly
cd cowly
```

### 2. Environment file

```bash
cp .env.example .env
```

Edit `.env` if needed (JWT secret, simulator herd size). Defaults work for local development.

### 3. Build and run

```bash
docker compose up --build
```

First startup creates Postgres databases via `docker/postgres/init-databases.sql` and each service runs schema migrations (`create_all`) on boot.

### 4. Verify health

```bash
curl http://localhost:8000/health
```

You should see all downstream services reported as `ok`.

### 5. Open API docs

- Gateway: [http://localhost:8000](http://localhost:8000)
- Auth: [http://localhost:8102/docs](http://localhost:8102/docs)
- Herd: [http://localhost:8103/docs](http://localhost:8103/docs)

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
| `COWLY_AUTH_JWT_SECRET` | Shared secret for JWT signing (all services + gateway) |
| `COWLY_COLLAR_SIM_HERD_SIZE` | Number of simulated collars seeded on startup |
| `COWLY_INTERNAL_API_KEY` | Service-to-service key (alert → notification) |

Inside Docker, each service receives its own `DATABASE_URL` pointing at `postgres:5432/<db_name>`.  
On the host machine, Postgres is reachable at `localhost:5433`.

---

## Authentication

Protected routes require a Bearer token from login.

**Public (no token):**

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /health`

**Protected:** all other `/api/v1/*` routes through the gateway.

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
├── docs/
│   ├── images/            # Screenshots & diagrams (see Demo section)
│   └── videos/            # Walkthrough videos
├── scripts/
│   └── run_all_tests.sh
├── docker-compose.yml
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

### Per-service unit tests (SQLite, no Docker required)

Uses in-memory SQLite; runs inside Docker if local Python is unavailable.

```bash
./scripts/run_all_tests.sh
```

Or a single service:

```bash
cd auth-service
pip install -r requirements-dev.txt
COWLY_AUTH_DATABASE_URL=sqlite:// pytest -q tests/
```

### Integration tests (full stack)

Start the stack first, then:

```bash
RUN_INTEGRATION=1 ./scripts/run_all_tests.sh
```

Integration tests call `http://localhost:8000` and exercise register → herd → collars → telemetry → alerts end-to-end.

---

## Local development (without Docker)

1. Start Postgres (or use `docker compose up postgres -d` only).
2. Ensure databases exist (`docker/postgres/init-databases.sql`).
3. In each service directory:

```bash
cd auth-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export COWLY_AUTH_DATABASE_URL=postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_auth
python run.py
```

Repeat for other services with their ports and `DATABASE_URL` values from `docker-compose.yml`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `address already in use` on port 5432 | Host Postgres conflicts; Cowly maps Postgres to **5433** |
| Services connect to `localhost:5433` inside Docker | Rebuild after `docker-compose.yml` fix; URLs must use host `postgres:5432` in containers |
| `database "cowly_auth" does not exist` | Reset volume: `docker volume rm cowly_postgres_data` and `docker compose up --build` |
| `401 Not authenticated` | Login first; pass `Authorization: Bearer <token>` on protected routes |
| Auth register returns 500 (bcrypt) | Rebuild auth-service image after dependency updates |

---

## Roadmap

- [ ] Mobile / web client application
- [ ] Alembic migrations per service
- [ ] Geofence service & map UI
- [ ] Real IoT ingestion (MQTT) replacing simulator
- [ ] Redis-backed job queues for notifications
- [ ] Kubernetes / production deployment manifests
- [ ] Screenshots & video docs in `docs/images` and `docs/videos`

---

## License

<!-- Add your license here, e.g. MIT, Apache-2.0 -->

*License TBD.*
