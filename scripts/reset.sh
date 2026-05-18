#!/usr/bin/env bash
# Stop Cowly and remove all persisted data (PostgreSQL volume). Requires confirmation.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "WARNING: This stops Cowly and deletes ALL database data (postgres volume)."
read -r -p "Type 'reset' to continue: " confirm
if [[ "$confirm" != "reset" ]]; then
  echo "Aborted."
  exit 0
fi

docker compose -f docker-compose.yml down
docker volume rm cowly_postgres_data 2>/dev/null || docker volume rm "$(basename "$ROOT")_postgres_data" 2>/dev/null || true

echo "Cowly data reset. Run 'make up' or './scripts/setup.sh' to start fresh."
