$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Helpdesk Lite" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$backendDir = Join-Path $Root "backend"
if (-not (Test-Path "$backendDir\venv")) {
  Write-Host "[1/4] Создаю виртуальное окружение..." -ForegroundColor Yellow
  Push-Location $backendDir
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  Pop-Location
}

Write-Host "[1/4] Запускаю Backend..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory $backendDir -WindowStyle Normal -ArgumentList @(
  "-NoExit",
  "-Command",
  ".\venv\Scripts\Activate.ps1; pip install -r requirements.txt; alembic upgrade head; python seed.py; alembic stamp head; uvicorn app.main:app --reload"
)

Start-Sleep -Seconds 5

$frontendDir = Join-Path $Root "frontend"
Write-Host "[2/4] Запускаю Frontend..." -ForegroundColor Yellow
if (-not (Test-Path "$frontendDir\node_modules")) {
  Write-Host "  npm install..." -ForegroundColor Gray
}
Start-Process powershell -WorkingDirectory $frontendDir -WindowStyle Normal -ArgumentList @(
  "-NoExit",
  "-Command",
  "npm install; npm run dev"
)

Write-Host "[3/4] Открываю браузер..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Проект запущен!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "  Swagger:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Закройте окна Backend и Frontend для остановки." -ForegroundColor Gray
Write-Host ""
pause
