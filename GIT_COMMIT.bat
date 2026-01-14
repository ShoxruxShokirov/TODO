@echo off
chcp 65001 >nul
echo ============================================
echo    Git Commit and Push
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Adding all files...
git add -A
echo.

echo [2/3] Creating commit...
git commit -m "Add progress bar, statistics dashboard, and improved UI/UX features"
echo.

echo [3/3] Pushing to GitHub...
git push origin main
echo.

echo ============================================
echo    Done! Changes pushed to GitHub
echo ============================================
echo.
pause

