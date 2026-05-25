#!/usr/bin/env bash
set -euo pipefail

if [[ "${RUN_MIGRATIONS_ON_START:-0}" == "1" ]]; then
    echo "[entrypoint] Running alembic upgrade head..."
    alembic upgrade head
fi

exec "$@"
