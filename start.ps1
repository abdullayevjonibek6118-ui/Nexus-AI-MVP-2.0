# Nexus AI - PowerShell Launcher
# Запускает Backend и Frontend в отдельных окнах

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "     Nexus AI MVP - PowerShell Launcher" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Получаем путь к проекту
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath

# Останавливаем существующие процессы
Write-Host "[1/5] Остановка существующих процессов..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Nexus AI*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Проверка Python
Write-Host "[2/5] Проверка Python..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python найден: $pythonCheck" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python не найден! Установите Python 3.10+" -ForegroundColor Red
    pause
    exit
}

# Применение миграций
Write-Host "[3/5] Применение миграций базы данных..." -ForegroundColor Yellow
python migrate_db.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Миграции применены" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Ошибка при применении миграций (возможно, уже применены)" -ForegroundColor Yellow
}

# Запуск Backend
Write-Host "[4/5] Запуск Backend сервера..." -ForegroundColor Yellow
$backendPath = Join-Path $projectPath "backend"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$backendPath'; if (Test-Path 'venv\Scripts\activate.ps1') { .\venv\Scripts\activate.ps1 }; uvicorn app.main:app --reload --port 8000"
) -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "  ✓ Backend запущен на http://localhost:8000" -ForegroundColor Green

# Запуск Frontend
Write-Host "[5/5] Запуск Frontend сервера..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectPath "frontend"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$frontendPath'; python -m http.server 3000"
) -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "  ✓ Frontend запущен на http://localhost:3000" -ForegroundColor Green

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ✓ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Для остановки серверов закройте окна PowerShell" -ForegroundColor Yellow
Write-Host "или нажмите Ctrl+C в каждом окне" -ForegroundColor Yellow
Write-Host ""

# Открываем браузер
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
