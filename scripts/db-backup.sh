#!/usr/bin/env bash
# Backup all Cowly PostgreSQL databases from the running compose stack.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKUP_DIR="${1:-${ROOT}/backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${BACKUP_DIR}/${TIMESTAMP}"
mkdir -p "$OUT"

COMPOSE=(docker compose -f docker-compose.yml)
POSTGRES_SERVICE=postgres

if ! "${COMPOSE[@]}" ps --status running postgres 2>/dev/null | grep -q postgres; then
  echo "ERROR: postgres service is not running. Start the stack first: make up"
  exit 1
fi

DATABASES=(cowly_auth cowly_herd cowly_collar cowly_telemetry cowly_alerts cowly_notifications)

echo "==> Backing up to ${OUT}"
for db in "${DATABASES[@]}"; do
  echo "    ${db}"
  "${COMPOSE[@]}" exec -T "$POSTGRES_SERVICE" \
    pg_dump -U cowly -Fc "$db" > "${OUT}/${db}.dump"
done

echo "Backup complete: ${OUT}"
