#!/usr/bin/env bash
# Run all Cowly tests inside Docker (Python 3.11 service images).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Re-exec under docker group if user is in group but current shell is not (common after usermod).
if [ -z "${COWLY_DOCKER_GROUP_ACTIVE:-}" ]; then
  if ! docker info >/dev/null 2>&1; then
    if getent group docker | grep -qE "(^|:)${USER}(,|$)"; then
      echo "==> Activating docker group for this run (your shell has not picked it up yet)."
      echo "    Permanent fix: reboot, or run: newgrp docker"
      export COWLY_DOCKER_GROUP_ACTIVE=1
      export RUN_INTEGRATION="${RUN_INTEGRATION:-0}"
      exec sg docker -c "cd $(printf '%q' "$ROOT") && $(printf '%q' "$0")"
    fi
    echo "ERROR: Docker is required to run tests."
    echo "  Add yourself to docker:  sudo usermod -aG docker \$USER"
    echo "  Then reboot, or run:     newgrp docker"
    echo "  Verify:                groups | grep docker"
    exit 1
  fi
fi

COMPOSE=(docker compose -f docker-compose.yml)
COMPOSE_TEST=(docker compose -f docker-compose.yml -f docker-compose.test.yml)

SERVICES=(
  auth-service
  herd-service
  collar-registry
  telemetry-service
  alert-service
  notification-service
  collar-simulator
  api-gateway
)

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

env_to_docker_args() {
  local env_string=$1
  local -n out=$2
  out=()
  for pair in $env_string; do
    out+=(-e "$pair")
  done
}

run_service_tests() {
  local svc=$1
  local -a env_args
  env_to_docker_args "${TEST_ENV[$svc]}" env_args
  "${COMPOSE[@]}" run --rm --no-deps "${env_args[@]}" "$svc" \
    sh -c "pip install -q -r requirements-dev.txt && PYTHONPATH=. pytest -q tests/"
}

gateway_is_healthy() {
  "${COMPOSE[@]}" exec -T api-gateway python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" \
    >/dev/null 2>&1
}

wait_for_gateway() {
  local attempts="${COWLY_INTEGRATION_WAIT_ATTEMPTS:-90}"
  local i=0
  while [ "$i" -lt "$attempts" ]; do
    if gateway_is_healthy; then
      return 0
    fi
    sleep 2
    i=$((i + 1))
  done
  echo "ERROR: api-gateway did not become healthy in time."
  echo "  Inspect: docker compose ps"
  echo "  Logs:    docker compose logs api-gateway notification-service"
  return 1
}

start_stack() {
  if "${COMPOSE[@]}" up -d --wait 2>/dev/null; then
    gateway_is_healthy && return 0
  fi
  "${COMPOSE[@]}" up -d
  wait_for_gateway
}

ensure_stack_for_integration() {
  if gateway_is_healthy; then
    return 0
  fi
  if [ "${COWLY_INTEGRATION_NO_START:-0}" = "1" ]; then
    echo "ERROR: API gateway is not running."
    echo "  Start the stack: docker compose up -d   (or: make up)"
    echo "  Or unset COWLY_INTEGRATION_NO_START to auto-start."
    return 1
  fi
  echo "==> Starting stack for integration tests..."
  if start_stack; then
    return 0
  fi
  if [ "${COWLY_INTEGRATION_NO_RESET:-0}" = "1" ]; then
    return 1
  fi
  echo "==> Stack unhealthy (often stale Postgres schema); recreating database volume..."
  "${COMPOSE[@]}" down -v
  start_stack
}

run_integration_tests() {
  echo ""
  echo "==> Integration tests (via test-integration container, Python 3.11)"
  ensure_stack_for_integration || return 1
  "${COMPOSE_TEST[@]}" build test-integration
  "${COMPOSE_TEST[@]}" --profile test run --rm test-integration
}

echo "==> Cowly test suite (Docker / Python 3.11)"
echo "==> Building service images..."
"${COMPOSE[@]}" build "${SERVICES[@]}"

failed=()
for svc in "${SERVICES[@]}"; do
  echo ""
  echo "==> ${svc}"
  if run_service_tests "$svc"; then
    :
  else
    failed+=("$svc")
  fi
done

if [ "${RUN_INTEGRATION:-0}" = "1" ]; then
  if run_integration_tests; then
    :
  else
    failed+=("integration")
  fi
else
  echo ""
  echo "==> Skipping integration tests"
  echo "    Run E2E too: make test-integration"
fi

echo ""
if [ "${#failed[@]}" -gt 0 ]; then
  echo "FAILED: ${failed[*]}"
  exit 1
fi
echo "All tests passed."
