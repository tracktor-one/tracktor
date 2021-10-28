#!/bin/bash
set -ex

echo "Run migrations"
/usr/local/bin/python -m alembic upgrade head
echo "Starting tracktor"
/usr/local/bin/python -m uvicorn tracktor:app --host 0.0.0.0 --port 80
