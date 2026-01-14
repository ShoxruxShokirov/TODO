# 🚀 Deploy Django TODO App to Render.com

## Step 1: Prepare the Project

1. **Open PowerShell in the TODO folder:**
   ```bash
   cd C:\Users\User\Documents\Django\TODO
   ```

2. **Initialize Git (if not done yet):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```

3. **Create a repository on GitHub:**
   - Go to https://github.com
   - Click "New repository"
   - Name it `django-todo-app` (or any name you prefer)
   - Do NOT add README, .gitignore (they already exist)
   - Click "Create repository"

4. **Upload code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/django-todo-app.git
   git branch -M main
   git push -u origin main
   ```
   (Replace YOUR-USERNAME with your GitHub username)

## Step 2: Deploy to Render

1. **Go to Render:**
   - Open https://render.com
   - Sign up or log in (you can use GitHub)

2. **Create a new Web Service:**
   - Click "New +" in the top right corner
   - Select "Web Service"
   - Connect your GitHub repository `django-todo-app`

3. **Service Settings:**
   - **Name:** `django-todo-app` (or any name)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn todo_project.wsgi:application`

4. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable" and add:
   
   - **SECRET_KEY:**
     Generate one:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(50))"
     ```
     Copy the output and paste it as the value
   
   - **DEBUG:**
     Value: `False`
   
   - **ALLOWED_HOSTS:**
     Value: `your-app-name.onrender.com` (replace with your actual Render domain)

5. **Create Database (if using PostgreSQL):**
   - In Render Dashboard, click "New +"
   - Select "PostgreSQL"
   - Name it (e.g., `django-todo-db`)
   - Copy the Internal Database URL
   - Add it as environment variable `DATABASE_URL` in your Web Service settings

6. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)

## Step 3: Run Migrations

After the first deployment:

1. **Open Render Shell:**
   - Go to your Web Service in Render Dashboard
   - Click "Shell" tab
   - Or use Render CLI

2. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Step 4: Access Your App

- Your app will be available at: `https://your-app-name.onrender.com`
- Admin panel: `https://your-app-name.onrender.com/admin/`

## Troubleshooting

### Static Files Not Loading
- Make sure `collectstatic` runs in build command
- Check that `STATIC_ROOT` is set in settings.py
- Verify WhiteNoise middleware is in MIDDLEWARE

### Database Errors
- Make sure migrations are run
- Check database connection settings
- Verify environment variables are set

### 500 Internal Server Error
- Check Render logs in Dashboard
- Verify SECRET_KEY is set
- Check ALLOWED_HOSTS includes your domain
- Ensure DEBUG=False in production

### Build Fails
- Check that all files are in Git
- Verify requirements.txt exists in root
- Check Python version compatibility

## Environment Variables Summary

Required variables:
- `SECRET_KEY` - Django secret key (generate one)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your Render domain

Optional:
- `DATABASE_URL` - If using PostgreSQL
- `PYTHON_VERSION` - Python version (default: 3.11.0)

## Quick Reference

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn todo_project.wsgi:application
```

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

⭐ Your Django TODO App is now live on Render!

