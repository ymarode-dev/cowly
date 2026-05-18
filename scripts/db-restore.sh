#!/usr/bin/env bash
# Restore Cowly databases from a backup directory created by db-backup.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKUP_DIR="${1:-}"
if [[ -z "$BACKUP_DIR" || ! -d "$BACKUP_DIR" ]]; then
  echo "Usage: $0 <backup-directory>"
  echo "Example: $0 backups/20250118-120000"
  exit 1
fi

COMPOSE=(docker compose -f docker-compose.yml)
POSTGRES_SERVICE=postgres

if ! "${COMPOSE[@]}" ps --status running postgres 2>/dev/null | grep -q postgres; then
  echo "ERROR: postgres service is not running."
  exit 1
fi

echo "WARNING: This will overwrite data in all Cowly databases."
read -r -p "Continue? [y/N] " confirm
if [[ "${confirm,,}" != "y" ]]; then
  echo "Aborted."
  exit 0
fi

for dump in "${BACKUP_DIR}"/*.dump; do
  [[ -f "$dump" ]] || continue
  db="$(basename "$dump" .dump)"
  echo "==> Restoring ${db}"
  "${COMPOSE[@]}" exec -T "$POSTGRES_SERVICE" \
    pg_restore -U cowly -d "$db" --clean --if-exists < "$dump" || true
done

echo "Restore complete from ${BACKUP_DIR}"
