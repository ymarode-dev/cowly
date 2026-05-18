#!/usr/bin/env bash
# Run unit tests for one service in Docker (Python 3.11, PYTHONPATH=.).
# Usage: ./scripts/run_service_tests.sh auth-service
# Or:    make test-service SVC=auth-service
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SVC="${1:-}"
if [ -z "$SVC" ]; then
  echo "Usage: $0 <service-name>"
  echo "Example: $0 herd-service"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is required."
  exit 1
fi

COMPOSE=(docker compose -f docker-compose.yml)

declare -A TEST_ENV=(
  [auth-service]="COWLY_SKIP_MIGRATIONS=1 COWLY_AUTH_DATABASE_URL=sqlite:// COWLY_AUTH_REDIS_URL=redis://redis:6379/0"
  [herd-service]="COWLY_SKIP_MIGRATIONS=1 COWLY_HERD_DATABASE_URL=sqlite://"
  [collar-registry]="COWLY_SKIP_MIGRATIONS=1 COWLY_COLLAR_REGISTRY_DATABASE_URL=sqlite:// COWLY_COLLAR_REGISTRY_COLLAR_SIMULATOR_URL=http://simulator.test"
  [telemetry-service]="COWLY_SKIP_MIGRATIONS=1 COWLY_TELEMETRY_DATABASE_URL=sqlite:// COWLY_TELEMETRY_ALERT_SERVICE_URL=http://alert.test"
  [alert-service]="COWLY_SKIP_MIGRATIONS=1 COWLY_ALERT_DATABASE_URL=sqlite:// COWLY_ALERT_NOTIFICATION_SERVICE_URL=http://notification.test"
  [notification-service]="COWLY_SKIP_MIGRATIONS=1 COWLY_NOTIFICATION_DATABASE_URL=sqlite://"
  [collar-simulator]="COWLY_COLLAR_SIM_HERD_SIZE=20"
  [api-gateway]="COWLY_GATEWAY_REDIS_ENABLED=false"
)

if [ -z "${TEST_ENV[$SVC]+x}" ]; then
  echo "Unknown service: $SVC"
  exit 1
fi

env_args=()
for pair in ${TEST_ENV[$SVC]}; do
  env_args+=(-e "$pair")
done

echo "==> Building ${SVC}..."
"${COMPOSE[@]}" build "$SVC"
echo "==> Testing ${SVC} (Python 3.11 in container)..."
"${COMPOSE[@]}" run --rm --no-deps "${env_args[@]}" "$SVC" \
  sh -c "pip install -q -r requirements-dev.txt && PYTHONPATH=. pytest -q tests/"
