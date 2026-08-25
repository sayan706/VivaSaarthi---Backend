#!/bin/sh
set -e

echo "[entrypoint] waiting for database ${DB_HOST}:${DB_PORT}..."
python - <<'PY'
import os
import sys
import time

import psycopg2

host = os.environ.get('DB_HOST', 'localhost')
port = os.environ.get('DB_PORT', '5432')
user = os.environ.get('DB_USER', 'postgres')
password = os.environ.get('DB_PASSWORD', 'postgres')
dbname = os.environ.get('DB_NAME', 'vivasaarthi')

deadline = time.time() + 90
while True:
    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password,
            dbname=dbname, connect_timeout=3,
        )
        conn.close()
        break
    except psycopg2.OperationalError:
        if time.time() > deadline:
            sys.exit(f'database {host}:{port} not reachable within 90s')
        time.sleep(2)
PY
echo "[entrypoint] database is up."

# Create tables only if they are missing. A restored dump already contains the
# schema, so db.create_all() is a no-op and cannot conflict with it.
echo "[entrypoint] ensuring schema..."
python - <<'PY'
from sqlalchemy import inspect

from app import create_app, db
import app.models  # noqa: F401  # registers every table on db.metadata

app = create_app()
with app.app_context():
    existing = set(inspect(db.engine).get_table_names())
    missing = sorted(t for t in db.metadata.tables if t not in existing)
    if missing:
        db.create_all()
        print(f'[entrypoint] created missing tables: {", ".join(missing)}')
    else:
        print('[entrypoint] schema already present, skipping init.')
PY

# Flask-SocketIO production deployment: gunicorn with the gevent-websocket
# worker (requires gevent monkey-patching, done in run.py at import time).
# One worker: gevent is async, and socket.io needs sticky sessions across
# workers anyway. --timeout 300 tolerates slow DeepSeek/Gemini calls.
echo "[entrypoint] starting gunicorn..."
exec gunicorn \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    --workers 1 \
    --worker-connections 1000 \
    --timeout 300 \
    --graceful-timeout 60 \
    --error-logfile - \
    --bind 0.0.0.0:5000 \
    run:app
