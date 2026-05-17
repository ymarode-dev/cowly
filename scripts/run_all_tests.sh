#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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

declare -A SQLITE_ENV=(
  [auth-service]="COWLY_AUTH_DATABASE_URL=sqlite://"
  [herd-service]="COWLY_HERD_DATABASE_URL=sqlite://"
  [collar-registry]="COWLY_COLLAR_REGISTRY_DATABASE_URL=sqlite:// COWLY_COLLAR_REGISTRY_COLLAR_SIMULATOR_URL=http://simulator.test"
  [telemetry-service]="COWLY_TELEMETRY_DATABASE_URL=sqlite://"
  [alert-service]="COWLY_ALERT_DATABASE_URL=sqlite:// COWLY_ALERT_NOTIFICATION_SERVICE_URL=http://notification.test"
  [notification-service]="COWLY_NOTIFICATION_DATABASE_URL=sqlite://"
  [collar-simulator]="COWLY_COLLAR_SIM_HERD_SIZE=20"
  [api-gateway]=""
)

run_in_docker() {
  local svc=$1
  local extra_env="${SQLITE_ENV[$svc]}"
  docker compose run --rm --no-deps "$svc" sh -c "
    pip install -q pytest httpx respx 2>/dev/null || pip install -q pytest httpx
    ${extra_env}
    pytest -q tests/
  "
}

run_local() {
  local svc=$1
  local extra_env="${SQLITE_ENV[$svc]}"
  (
    cd "$ROOT/${svc}"
    python3 -m pip install -q -r requirements.txt
    python3 -m pip install -q pytest httpx respx 2>/dev/null || python3 -m pip install -q pytest httpx
    export ${extra_env}
    python3 -m pytest -q tests/
  )
}

use_docker=false
if docker info >/dev/null 2>&1; then
  use_docker=true
elif ! python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  echo "ERROR: Need Docker or Python 3.10+ to run tests."
  exit 1
fi

echo "==> Running per-service tests (via ${use_docker:+Docker}${use_docker:-local Python})"

for svc in "${SERVICES[@]}"; do
  echo ""
  echo "==> ${svc}"
  if [ "$use_docker" = true ]; then
    run_in_docker "$svc"
  else
    run_local "$svc"
  fi
done

if [ "${RUN_INTEGRATION:-0}" = "1" ]; then
  echo ""
  echo "==> Integration tests (gateway must be up)"
  python3 -m pip install -q -r requirements-test.txt
  python3 -m pytest -q integration/ -m integration
else
  echo ""
  echo "==> Skipping integration tests (set RUN_INTEGRATION=1 with docker compose up)"
fi

echo ""
echo "All per-service tests passed."
