@echo off
title Anclora PDF2EPUB - Configuracion Hibrida con Virtual Environment
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - CONFIGURACION HIBRIDA + VENV
echo =====================================================
echo.
echo Este script configura desarrollo hibrido con entorno virtual:
echo - Redis en Docker (evita problemas Windows)
echo - Virtual Environment Python activado
echo - Backend Python local (hot reload)
echo - Frontend React local (hot reload)
echo.

REM Verificar Docker
echo Verificando Docker...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no esta corriendo. Por favor inicialo.
    echo    Abre Docker Desktop y espera a que este listo.
    pause
    exit /b 1
)
echo OK: Docker listo

REM Verificar entorno virtual
echo Verificando entorno virtual...
if not exist "venv-py311\Scripts\activate.bat" (
    echo ERROR: No se encuentra el entorno virtual venv-py311
    echo    Ejecuta: python -m venv venv-py311
    pause
    exit /b 1
)
echo OK: Entorno virtual encontrado

REM Detener contenedores anteriores
echo Limpiando contenedores anteriores...
docker stop redis-anclora >nul 2>&1
docker rm redis-anclora >nul 2>&1

REM Iniciar Redis
echo Iniciando Redis en Docker...
docker run -d ^
    --name redis-anclora ^
    -p 6379:6379 ^
    redis:7-alpine ^
    redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes

if %errorlevel% neq 0 (
    echo ERROR: Error iniciando Redis
    pause
    exit /b 1
)

echo OK: Redis iniciado en puerto 6379

REM Esperar a que Redis este listo
echo Esperando que Redis este listo...
timeout /t 3 /nobreak >nul

REM Verificar conexion Redis
echo Verificando conexion Redis...
docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Redis no responde
    pause
    exit /b 1
)
echo OK: Redis respondiendo correctamente

echo.
echo =====================================================
echo CONFIGURACION HIBRIDA + VENV LISTA
echo =====================================================
echo.
echo Redis esta corriendo en Docker en puerto 6379
echo Entorno virtual: venv-py311
echo.
echo PROXIMOS PASOS:
echo.
echo === POWERSHELL ===
echo.
echo 1. ACTIVAR ENTORNO VIRTUAL:
echo    .\venv-py311\Scripts\Activate.ps1
echo.
echo 2. BACKEND (PowerShell con venv activado):
echo    cd backend
echo    pip install -r requirements.txt
echo    python main.py
echo.
echo 3. FRONTEND (Nueva PowerShell):
echo    cd frontend
echo    npm install
echo    npm start
echo.
echo 4. CELERY WORKER (PowerShell con venv activado):
echo    cd backend
echo    celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet
echo.
echo === CMD (si PowerShell da problemas) ===
echo.
echo 1. ACTIVAR ENTORNO VIRTUAL:
echo    venv-py311\Scripts\activate.bat
echo.
echo URLs una vez iniciado todo:
echo    Frontend: http://localhost:5178
echo    Backend:  http://localhost:5175
echo    Redis:    localhost:6379
echo.
echo DESACTIVAR ENTORNO VIRTUAL:
echo    deactivate
echo.
echo Para detener Redis: docker stop redis-anclora
echo.
pause