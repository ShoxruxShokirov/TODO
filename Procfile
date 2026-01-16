web: python manage.py migrate --noinput && python manage.py collectstatic --noinput || echo "Static files failed, continuing..." && gunicorn todo_project.wsgi:application

