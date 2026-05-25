@echo off
chcp 65001 >nul
title Helpdesk Lite Launcher

echo ============================================
echo   Helpdesk Lite - Fullstack запуск
echo ============================================
echo.

set ROOT=%~dp0

REM --- Backend ---
echo [1/3] Запускаю Backend (FastAPI)...
start "Backend" cmd /c "cd /d "%ROOT%backend" && .\venv\Scripts\activate && alembic upgrade head && python seed.py && alembic stamp head && uvicorn app.main:app --reload"

REM Ждём 5 секунд пока backend поднимется
timeout /t 5 /nobreak >nul

REM --- Frontend ---
echo [2/3] Запускаю Frontend (Vue 3)...
start "Frontend" cmd /c "cd /d "%ROOT%frontend" && npm install && npm run dev"

REM --- Browser ---
echo [3/3] Открываю браузер...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ============================================
echo   Проект запущен!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   Swagger:  http://localhost:8000/docs
echo ============================================
echo.
echo Закройте окна Backend и Frontend для остановки.
echo.
pause
