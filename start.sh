#!/bin/bash
set -e

echo "=========================================="
echo "Starting Django TODO App Deployment"
echo "=========================================="

echo "Step 1: Running migrations..."
python manage.py migrate --noinput || {
    echo "ERROR: Migrations failed!"
    exit 1
}

echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "WARNING: Static files collection failed, continuing..."
}

echo "Step 3: Starting Gunicorn..."
exec gunicorn todo_project.wsgi:application

