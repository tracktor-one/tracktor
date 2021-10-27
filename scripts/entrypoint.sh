#!/bin/sh

/usr/local/bin/python -m alembic upgrade head
/usr/local/bin/python -m uvicorn tracktor:app --host 0.0.0.0 --port 80
