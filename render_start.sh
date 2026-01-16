#!/usr/bin/env bash
set -o errexit  # Exit on error
set -o nounset  # Exit on unset variable

echo "=========================================="
echo "Django TODO App - Starting Deployment"
echo "=========================================="

# Step 1: Run migrations (CRITICAL - must succeed)
echo ""
echo ">>> Step 1: Running database migrations..."
python manage.py migrate --noinput
MIGRATE_STATUS=$?

if [ $MIGRATE_STATUS -ne 0 ]; then
    echo "ERROR: Database migrations failed with exit code $MIGRATE_STATUS"
    echo "This is a critical error. Exiting..."
    exit 1
fi

echo "✓ Migrations completed successfully"

# Step 2: Collect static files (non-critical, can fail)
echo ""
echo ">>> Step 2: Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "WARNING: Static files collection failed, but continuing..."
}

# Step 3: Start Gunicorn
echo ""
echo ">>> Step 3: Starting Gunicorn server..."
echo "=========================================="
exec gunicorn todo_project.wsgi:application

