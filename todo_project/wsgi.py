"""
WSGI config for todo_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_project.settings')

from django.core.wsgi import get_wsgi_application
from django.db import connection

logger = logging.getLogger('tasks')

# Получаем WSGI application
application = get_wsgi_application()

# Автоматическая проверка и выполнение миграций при старте
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
        table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        logger.warning("=" * 60)
        logger.warning("WARNING: Database tables not found on startup!")
        logger.warning("Auto-running migrations in wsgi.py...")
        logger.warning("=" * 60)
        
        from django.core.management import call_command
        call_command('migrate', verbosity=2, interactive=False)
        logger.info("✓ Migrations completed successfully in wsgi.py")
    else:
        logger.debug("Database tables exist, migrations not needed on startup")
except Exception as e:
    logger.error(f"ERROR in wsgi.py migration check: {e}")
    # Не прерываем запуск, продолжаем работу

