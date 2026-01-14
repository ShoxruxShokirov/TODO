# 🔧 Исправление ошибки: no such table: auth_user

## Проблема:
На Render не выполнены миграции базы данных, поэтому таблицы не созданы.

## Решение:

### Вариант 1: Через Build Command (рекомендуется)

В Render Dashboard → Settings → Build & Deploy:

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

**Start Command:**
```
gunicorn todo_project.wsgi:application
```

### Вариант 2: Через Start Command

Если миграции не выполняются в Build Command, добавьте их в Start Command:

**Start Command:**
```
python manage.py migrate --noinput && gunicorn todo_project.wsgi:application
```

### Вариант 3: Через Shell (вручную)

1. В Render Dashboard откройте ваш сервис
2. Перейдите на вкладку **"Shell"**
3. Выполните команды:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## Также исправьте DEBUG:

В Render Dashboard → Environment Variables:

Добавьте переменную:
- **KEY:** `DEBUG`
- **VALUE:** `False`

Это важно для безопасности в production!

---

## После исправления:

1. Сохраните изменения
2. Нажмите **"Manual Deploy"** → **"Deploy latest commit"**
3. Дождитесь завершения деплоя

После этого сайт должен работать!

