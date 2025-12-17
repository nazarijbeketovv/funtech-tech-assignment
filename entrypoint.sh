#!/bin/bash
set -e

if [ "$1" = "python3" ] && [[ "$*" == *"gunicorn"* ]]; then
    echo "Running database migrations..."
    cd /app
    . .venv/bin/activate
    
    if [ ! -d "src/infra/db/migrations" ]; then
        echo "ERROR: Migrations directory not found at src/infra/db/migrations"
        echo "Current directory: $(pwd)"
        echo "Contents of /app:"
        ls -la /app
        echo "Contents of /app/src (if exists):"
        [ -d /app/src ] && ls -la /app/src || echo "src directory does not exist"
        exit 1
    fi
    
    PYTHONPATH=src alembic -c alembic.ini upgrade head
    echo "Migrations completed. Starting application..."
fi

exec "$@"
