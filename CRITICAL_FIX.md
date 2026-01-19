# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ - ОБЯЗАТЕЛЬНО ВЫПОЛНИТЬ!

## Проблема
Ошибка 500 возникает, если миграция `0003_task_tags_task_color.py` не применена на сервере.

## Решение

### На сервере Render.com:

1. **Зайдите в Render Dashboard** → ваш сервис
2. **Shell** (или используйте команду в Build Command):
   ```bash
   python manage.py migrate
   ```

### Или добавьте в `render.yaml`:
```yaml
services:
  - type: web
    buildCommand: python manage.py migrate --noinput && ...
```

### Локально проверьте:
```bash
cd TODO
python manage.py migrate
python manage.py check
python manage.py runserver
```

## После применения миграции
Сайт должен заработать. Поля `tags` и `color` будут доступны.

## Если миграцию нельзя применить
Код защищен от ошибок, но поля `tags` и `color` будут недоступны до применения миграции.

