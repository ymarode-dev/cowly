#!/usr/bin/env bash
# Generate pinned requirements.lock for each Python service.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SERVICES=(
  api-gateway
  auth-service
  herd-service
  collar-registry
  collar-simulator
  telemetry-service
  alert-service
  notification-service
  seed-service
)

for svc in "${SERVICES[@]}"; do
  dir="${ROOT}/${svc}"
  [[ -f "${dir}/requirements.txt" ]] || continue
  echo "==> ${svc}"
  python3 -m pip install -q -r "${dir}/requirements.txt"
  python3 -m pip freeze --exclude-editable > "${dir}/requirements.lock"
done

echo "requirements.lock written for all services."
