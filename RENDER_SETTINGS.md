# ⚙️ Render Settings Configuration

## Правильные настройки для Django TODO App

### 1. Environment (Окружение)
- **Environment:** `Python 3` (обязательно выберите Python!)

### 2. Build Command (Команда сборки)
Замените команду Go на:
```
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### 3. Start Command (Команда запуска)
Замените команду Go на:
```
gunicorn todo_project.wsgi:application
```

### 4. Branch (Ветка)
- **Branch:** `main`

### 5. Root Directory (Корневая директория)
- **Root Directory:** (оставьте ПУСТЫМ!)

### 6. Region (Регион)
- **Region:** Выберите ближайший к вам (например, Oregon для США)

---

## 📋 Полная конфигурация

**Environment:** Python 3  
**Build Command:** `pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput`  
**Start Command:** `gunicorn todo_project.wsgi:application`  
**Branch:** `main`  
**Root Directory:** (пусто)

---

## ⚠️ Важно!

Если вы видите команды Go (`go build` и `./app`), это означает, что Render не определил тип проекта автоматически. Вы должны:

1. Выбрать **Environment: Python 3** вручную
2. Заменить команды на команды для Django (указаны выше)

После этого сохраните настройки и деплой должен пройти успешно.

