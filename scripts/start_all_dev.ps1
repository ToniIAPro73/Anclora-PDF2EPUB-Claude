# Anclora PDF2EPUB - Inicio Automatico PowerShell
param(
    [string]$TerminalApp = "auto"  # "auto", "cmd", "powershell", "wt" (Windows Terminal)
)

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "ANCLORA PDF2EPUB - INICIO AUTOMATICO COMPLETO" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script va a:" -ForegroundColor Yellow
Write-Host "1. Configurar Redis en Docker" -ForegroundColor White
Write-Host "2. Abrir 3 terminales automaticamente:" -ForegroundColor White
Write-Host "   - Backend (con venv activado)" -ForegroundColor White
Write-Host "   - Frontend (npm start)" -ForegroundColor White
Write-Host "   - Celery Worker (con venv activado)" -ForegroundColor White
Write-Host ""

# Obtener directorio actual
$currentDir = Get-Location

# Verificar Docker
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    $null = docker version 2>$null
    Write-Host "OK: Docker listo" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker no esta corriendo. Por favor inicialo." -ForegroundColor Red
    Write-Host "    Abre Docker Desktop y espera a que este listo." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar entorno virtual
Write-Host "Verificando entorno virtual..." -ForegroundColor Yellow
if (!(Test-Path "venv-py311\Scripts\Activate.ps1")) {
    Write-Host "ERROR: No se encuentra el entorno virtual venv-py311" -ForegroundColor Red
    Write-Host "    Ejecuta: python -m venv venv-py311" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "OK: Entorno virtual encontrado" -ForegroundColor Green

# Limpiar contenedores anteriores
Write-Host "Limpiando contenedores anteriores..." -ForegroundColor Yellow
docker stop redis-anclora 2>$null | Out-Null
docker rm redis-anclora 2>$null | Out-Null

# Iniciar Redis
Write-Host "Iniciando Redis en Docker..." -ForegroundColor Yellow
try {
    $null = docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes
    Write-Host "OK: Redis iniciado en puerto 6379" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Error iniciando Redis" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Esperar Redis
Write-Host "Esperando que Redis este listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verificar Redis
Write-Host "Verificando conexion Redis..." -ForegroundColor Yellow
try {
    $null = docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping 2>$null
    Write-Host "OK: Redis respondiendo correctamente" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Redis no responde" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "ABRIENDO TERMINALES AUTOMATICAMENTE..." -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Determinar que terminal usar
$useWindowsTerminal = $false
$usePowerShell = $false

if ($TerminalApp -eq "auto") {
    # Detectar Windows Terminal
    if (Get-Command "wt" -ErrorAction SilentlyContinue) {
        $useWindowsTerminal = $true
    } elseif (Get-Command "powershell" -ErrorAction SilentlyContinue) {
        $usePowerShell = $true
    }
} elseif ($TerminalApp -eq "wt") {
    $useWindowsTerminal = $true
} elseif ($TerminalApp -eq "powershell") {
    $usePowerShell = $true
}

# Scripts para cada terminal
$backendScript = @"
Write-Host '=================================='
Write-Host 'BACKEND SERVER - Puerto 5175' -ForegroundColor Green
Write-Host '=================================='
Write-Host ''
Set-Location '$currentDir'
& .\venv-py311\Scripts\Activate.ps1
Set-Location backend
Write-Host 'Instalando dependencias...' -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host ''
Write-Host 'Iniciando servidor Flask...' -ForegroundColor Yellow
python main.py
Read-Host 'Presiona Enter para cerrar'
"@

$frontendScript = @"
Write-Host '=================================='
Write-Host 'FRONTEND SERVER - Puerto 5178' -ForegroundColor Blue
Write-Host '=================================='
Write-Host ''
Set-Location '$currentDir\frontend'
Write-Host 'Instalando dependencias...' -ForegroundColor Yellow
npm install
Write-Host ''
Write-Host 'Iniciando servidor Vite...' -ForegroundColor Yellow
npm start
Read-Host 'Presiona Enter para cerrar'
"@

$celeryScript = @"
Write-Host '=================================='
Write-Host 'CELERY WORKER - Conversiones PDF' -ForegroundColor Magenta
Write-Host '=================================='
Write-Host ''
Set-Location '$currentDir'
& .\venv-py311\Scripts\Activate.ps1
Set-Location backend
Write-Host 'Esperando 10 segundos para que el backend este listo...' -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ''
Write-Host 'Iniciando Celery Worker...' -ForegroundColor Yellow
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
Read-Host 'Presiona Enter para cerrar'
"@

# Crear archivos temporales
$backendScript | Out-File -FilePath "temp_backend.ps1" -Encoding UTF8
$frontendScript | Out-File -FilePath "temp_frontend.ps1" -Encoding UTF8
$celeryScript | Out-File -FilePath "temp_celery.ps1" -Encoding UTF8

# Abrir terminales
if ($useWindowsTerminal) {
    Write-Host "Usando Windows Terminal..." -ForegroundColor Green

    Write-Host "Abriendo terminal Backend..." -ForegroundColor Yellow
    Start-Process "wt" -ArgumentList "new-tab", "--title", "Backend", "powershell", "-ExecutionPolicy", "Bypass", "-File", "temp_backend.ps1"

    Start-Sleep -Seconds 2

    Write-Host "Abriendo terminal Frontend..." -ForegroundColor Yellow
    Start-Process "wt" -ArgumentList "new-tab", "--title", "Frontend", "powershell", "-ExecutionPolicy", "Bypass", "-File", "temp_frontend.ps1"

    Start-Sleep -Seconds 2

    Write-Host "Abriendo terminal Celery..." -ForegroundColor Yellow
    Start-Process "wt" -ArgumentList "new-tab", "--title", "Celery", "powershell", "-ExecutionPolicy", "Bypass", "-File", "temp_celery.ps1"

} elseif ($usePowerShell) {
    Write-Host "Usando PowerShell..." -ForegroundColor Green

    Write-Host "Abriendo terminal Backend..." -ForegroundColor Yellow
    Start-Process "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "temp_backend.ps1"

    Start-Sleep -Seconds 2

    Write-Host "Abriendo terminal Frontend..." -ForegroundColor Yellow
    Start-Process "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "temp_frontend.ps1"

    Start-Sleep -Seconds 2

    Write-Host "Abriendo terminal Celery..." -ForegroundColor Yellow
    Start-Process "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "temp_celery.ps1"

} else {
    Write-Host "Usando CMD..." -ForegroundColor Green

    # Crear versiones CMD de los scripts
    @"
@echo off
title Anclora - Backend Server
echo ==================================
echo BACKEND SERVER - Puerto 5175
echo ==================================
echo.
cd /d "$currentDir"
call venv-py311\Scripts\activate.bat
cd backend
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando servidor Flask...
python main.py
pause
"@ | Out-File -FilePath "temp_backend.bat" -Encoding ASCII

    @"
@echo off
title Anclora - Frontend Server
echo ==================================
echo FRONTEND SERVER - Puerto 5178
echo ==================================
echo.
cd /d "$currentDir\frontend"
echo Instalando dependencias...
npm install
echo.
echo Iniciando servidor Vite...
npm start
pause
"@ | Out-File -FilePath "temp_frontend.bat" -Encoding ASCII

    @"
@echo off
title Anclora - Celery Worker
echo ==================================
echo CELERY WORKER - Conversiones PDF
echo ==================================
echo.
cd /d "$currentDir"
call venv-py311\Scripts\activate.bat
cd backend
echo Esperando 10 segundos para que el backend este listo...
timeout /t 10 /nobreak
echo.
echo Iniciando Celery Worker...
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
pause
"@ | Out-File -FilePath "temp_celery.bat" -Encoding ASCII

    Write-Host "Abriendo terminal Backend..." -ForegroundColor Yellow
    Start-Process "cmd" -ArgumentList "/c", "temp_backend.bat"

    Start-Sleep -Seconds 2

    Write-Host "Abriendo terminal Frontend..." -ForegroundColor Yellow
    Start-Process "cmd" -ArgumentList "/c", "temp_frontend.bat"

    Start-Sleep -Seconds 2

    Write-Host "Abriendo terminal Celery..." -ForegroundColor Yellow
    Start-Process "cmd" -ArgumentList "/c", "temp_celery.bat"
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "DESARROLLO INICIADO AUTOMATICAMENTE" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se han abierto 3 terminales:" -ForegroundColor Green
Write-Host "  [1] Backend  - http://localhost:5175 (Flask + venv)" -ForegroundColor White
Write-Host "  [2] Frontend - http://localhost:5178 (React + Vite)" -ForegroundColor White
Write-Host "  [3] Celery   - Worker para conversiones (venv)" -ForegroundColor White
Write-Host ""
Write-Host "Redis esta corriendo en: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "ACCEDER A LA APLICACION:" -ForegroundColor Yellow
Write-Host "  -> http://localhost:5178" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para DETENER todo:" -ForegroundColor Yellow
Write-Host "  1. Cierra las 3 terminales (Ctrl+C en cada una)" -ForegroundColor White
Write-Host "  2. Ejecuta: docker stop redis-anclora" -ForegroundColor White
Write-Host ""

# Limpiar archivos temporales después de 60 segundos
Write-Host "Limpiando archivos temporales en 60 segundos..." -ForegroundColor Gray
Start-Sleep -Seconds 60

Remove-Item "temp_backend.ps1" -ErrorAction SilentlyContinue
Remove-Item "temp_frontend.ps1" -ErrorAction SilentlyContinue
Remove-Item "temp_celery.ps1" -ErrorAction SilentlyContinue
Remove-Item "temp_backend.bat" -ErrorAction SilentlyContinue
Remove-Item "temp_frontend.bat" -ErrorAction SilentlyContinue
Remove-Item "temp_celery.bat" -ErrorAction SilentlyContinue

Read-Host "Presiona Enter para cerrar"