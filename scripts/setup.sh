#!/usr/bin/env bash
# One-command local bootstrap: env file, build, health wait, optional demo seed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose)
if [[ -f docker-compose.yml ]]; then
  COMPOSE+=(-f docker-compose.yml)
fi

SEED=false
DETACH=true
for arg in "$@"; do
  case "$arg" in
    --seed) SEED=true ;;
    --foreground|-f) DETACH=false ;;
  esac
done

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running. Start Docker and try again."
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
  echo "    Edit .env to set COWLY_AUTH_JWT_SECRET before any shared deployment."
else
  echo "==> Using existing .env"
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

COWLY_VERSION="${COWLY_VERSION:-$(tr -d '[:space:]' < VERSION 2>/dev/null || echo 0.1.0)}"
export COWLY_VERSION
export COWLY_BUILD_TIMESTAMP="${COWLY_BUILD_TIMESTAMP:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
export COWLY_VCS_REF="${COWLY_VCS_REF:-$(git rev-parse --short HEAD 2>/dev/null || echo unknown)}"

echo "==> Building and starting Cowly ${COWLY_VERSION}"
if [[ "$DETACH" == true ]]; then
  "${COMPOSE[@]}" up --build -d
else
  "${COMPOSE[@]}" up --build
  exit 0
fi

GATEWAY_PORT="${COWLY_GATEWAY_PORT:-8000}"
HEALTH_URL="http://localhost:${GATEWAY_PORT}/health"
echo "==> Waiting for gateway health at ${HEALTH_URL}"

deadline=$((SECONDS + 180))
until curl -sf "$HEALTH_URL" >/dev/null 2>&1; do
  if (( SECONDS >= deadline )); then
    echo "ERROR: Gateway did not become healthy within 180s"
    "${COMPOSE[@]}" ps
    exit 1
  fi
  sleep 3
done

curl -sf "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || curl -sf "$HEALTH_URL"
echo ""

if [[ "$SEED" == true ]]; then
  echo "==> Seeding demo data"
  "${COMPOSE[@]}" --profile seed up cowly-seed
fi

echo ""
echo "Cowly is running."
echo "  Gateway:  http://localhost:${GATEWAY_PORT}"
echo "  API docs: http://localhost:${GATEWAY_PORT}/docs"
echo "  Version:  http://localhost:${GATEWAY_PORT}/version"
echo ""
echo "Demo seed:  ./scripts/setup.sh --seed   or   make seed"
