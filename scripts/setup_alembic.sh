#!/usr/bin/env bash
# Install Alembic scaffolding into each database-backed service.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SERVICES=(auth-service herd-service collar-registry telemetry-service alert-service notification-service)

for svc in "${SERVICES[@]}"; do
  dir="${ROOT}/${svc}"
  echo "==> ${svc}"
  mkdir -p "${dir}/alembic/versions"
  cp "${ROOT}/docker/alembic/env.py.template" "${dir}/alembic/env.py"
  cp "${ROOT}/docker/alembic/001_initial_schema.py.template" "${dir}/alembic/versions/001_initial_schema.py"
  cat > "${dir}/alembic.ini" <<EOF
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF
done

echo "Alembic scaffolding installed. Each service env.py imports models via app.database."
