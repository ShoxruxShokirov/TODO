@echo off
chcp 65001 >nul
title Django TODO App
cls

echo.
echo ============================================
echo    Django TODO App - Starting Server
echo ============================================
echo.

cd /d "%~dp0"

REM Check Python
where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=py
    goto :found_python
)

where python >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    goto :found_python
)

echo [ERROR] Python not found!
echo Please install Python from https://www.python.org/
pause
exit /b 1

:found_python
echo [OK] Using: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo [1/3] Checking Django...
%PYTHON_CMD% -c "import django; print('[OK] Django', django.get_version())" 2>nul
if %errorlevel% neq 0 (
    echo [INSTALL] Installing Django...
    %PYTHON_CMD% -m pip install Django
)
echo.

echo [2/3] Running migrations...
%PYTHON_CMD% manage.py migrate --noinput
echo.

echo [3/3] Starting server...
echo.
echo ============================================
echo    SERVER IS STARTING...
echo ============================================
echo.
echo    URL: http://127.0.0.1:8000/
echo.
echo    Opening browser in 3 seconds...
echo    Press Ctrl+C to stop the server
echo ============================================
echo.

timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000/

echo.
%PYTHON_CMD% manage.py runserver 127.0.0.1:8000

pause

