@echo off
title Anclora PDF2EPUB - Configuracion Hibrida
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - CONFIGURACION HIBRIDA
echo =====================================================
echo.
echo Este script configura desarrollo hibrido:
echo - Redis en Docker (evita problemas Windows)
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
echo CONFIGURACION HIBRIDA LISTA
echo =====================================================
echo.
echo Redis esta corriendo en Docker en puerto 6379
echo.
echo PROXIMOS PASOS:
echo.
echo 1. BACKEND (Terminal 1):
echo    cd backend
echo    pip install -r requirements.txt
echo    python main.py
echo.
echo 2. FRONTEND (Terminal 2):
echo    cd frontend
echo    npm install
echo    npm start
echo.
echo 3. CELERY WORKER (Terminal 3 - Opcional):
echo    cd backend
echo    pip install eventlet
echo    celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet
echo.
echo URLs una vez iniciado todo:
echo    Frontend: http://localhost:5178
echo    Backend:  http://localhost:5175
echo    Redis:    localhost:6379
echo.
echo Para detener Redis: docker stop redis-anclora
echo.
pause