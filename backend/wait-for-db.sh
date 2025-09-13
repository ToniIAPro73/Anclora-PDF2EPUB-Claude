#!/bin/sh
# wait-for-db.sh - wait until PostgreSQL is ready
set -e

until python - <<'PY'
import os, sys, psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
except Exception:
    sys.exit(1)
PY
 do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

echo "PostgreSQL is up - executing command"
exec "$@"
