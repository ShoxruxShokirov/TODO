"""
Middleware для автоматического выполнения миграций при первом запуске.
Это резервный механизм на случай, если миграции не были выполнены при деплое.
"""
import logging
import os
from django.db import connection
from django.core.management import call_command
from django.core.exceptions import ImproperlyConfigured
from django.db.utils import OperationalError

logger = logging.getLogger('tasks')

# Флаг для предотвращения повторных попыток миграций
_migrations_checked = False
_migrations_running = False


class AutoMigrationMiddleware:
    """
    Middleware, который автоматически выполняет миграции при первом запросе,
    если обнаруживает отсутствие таблиц в базе данных.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        global _migrations_checked, _migrations_running
        
        # Выполняем проверку только один раз при инициализации middleware
        if not _migrations_checked and not _migrations_running:
            self.check_and_run_migrations()
    
    def check_and_run_migrations(self):
        """Проверяет наличие таблиц и выполняет миграции при необходимости."""
        global _migrations_checked, _migrations_running
        
        if _migrations_checked or _migrations_running:
            return
        
        _migrations_running = True
        
        try:
            # Проверяем наличие таблицы auth_user
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
                table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                logger.warning("=" * 60)
                logger.warning("WARNING: Database tables not found!")
                logger.warning("Auto-running migrations via middleware...")
                logger.warning("=" * 60)
                
                # Выполняем миграции
                try:
                    call_command('migrate', verbosity=2, interactive=False)
                    logger.info("✓ Migrations completed successfully via middleware")
                except Exception as e:
                    logger.error(f"ERROR: Failed to run migrations via middleware: {e}")
                    raise
            else:
                logger.debug("Database tables exist, migrations not needed")
                
        except OperationalError as e:
            # Если это ошибка "no such table", попробуем выполнить миграции
            if 'no such table' in str(e).lower():
                logger.warning("Detected 'no such table' error, attempting migrations...")
                try:
                    call_command('migrate', verbosity=2, interactive=False)
                    logger.info("✓ Migrations completed successfully via middleware (after error)")
                except Exception as e2:
                    logger.error(f"ERROR: Failed to run migrations after error: {e2}")
        except Exception as e:
            logger.error(f"ERROR: Unexpected error in migration check: {e}")
        finally:
            _migrations_checked = True
            _migrations_running = False
    
    def __call__(self, request):
        # При первом запросе, если миграции еще не проверялись, проверяем
        global _migrations_checked, _migrations_running
        
        if not _migrations_checked and not _migrations_running:
            # Не выполняем в __call__, чтобы не блокировать запросы
            # Вместо этого используем фоновую проверку при инициализации
            pass
        
        response = self.get_response(request)
        return response

