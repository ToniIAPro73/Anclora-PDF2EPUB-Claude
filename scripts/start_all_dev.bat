@echo off
title Anclora PDF2EPUB - Inicio Automatico de Desarrollo
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - INICIO AUTOMATICO COMPLETO
echo =====================================================
echo.
echo Este script va a:
echo 1. Configurar Redis en Docker
echo 2. Abrir 3 terminales automaticamente:
echo    - Backend (con venv activado)
echo    - Frontend (npm start)
echo    - Celery Worker (con venv activado)
echo.

REM Obtener ruta actual
set CURRENT_DIR=%CD%

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
echo ABRIENDO TERMINALES AUTOMATICAMENTE...
echo =====================================================
echo.

REM Crear scripts temporales para cada terminal
echo @echo off > temp_backend.bat
echo title Anclora - Backend Server >> temp_backend.bat
echo cd /d "%CURRENT_DIR%" >> temp_backend.bat
echo call venv-py311\Scripts\activate.bat >> temp_backend.bat
echo cd backend >> temp_backend.bat
echo echo. >> temp_backend.bat
echo echo ================================== >> temp_backend.bat
echo echo BACKEND SERVER - Puerto 5175 >> temp_backend.bat
echo echo ================================== >> temp_backend.bat
echo echo. >> temp_backend.bat
echo echo Instalando dependencias... >> temp_backend.bat
echo pip install -r requirements.txt >> temp_backend.bat
echo echo. >> temp_backend.bat
echo echo Iniciando servidor Flask... >> temp_backend.bat
echo python main.py >> temp_backend.bat
echo pause >> temp_backend.bat

echo @echo off > temp_frontend.bat
echo title Anclora - Frontend Server >> temp_frontend.bat
echo cd /d "%CURRENT_DIR%" >> temp_frontend.bat
echo cd frontend >> temp_frontend.bat
echo echo. >> temp_frontend.bat
echo echo ================================== >> temp_frontend.bat
echo echo FRONTEND SERVER - Puerto 5178 >> temp_frontend.bat
echo echo ================================== >> temp_frontend.bat
echo echo. >> temp_frontend.bat
echo echo Instalando dependencias... >> temp_frontend.bat
echo npm install >> temp_frontend.bat
echo echo. >> temp_frontend.bat
echo echo Iniciando servidor Vite... >> temp_frontend.bat
echo npm start >> temp_frontend.bat
echo pause >> temp_frontend.bat

echo @echo off > temp_celery.bat
echo title Anclora - Celery Worker >> temp_celery.bat
echo cd /d "%CURRENT_DIR%" >> temp_celery.bat
echo call venv-py311\Scripts\activate.bat >> temp_celery.bat
echo cd backend >> temp_celery.bat
echo echo. >> temp_celery.bat
echo echo ================================== >> temp_celery.bat
echo echo CELERY WORKER - Conversiones PDF >> temp_celery.bat
echo echo ================================== >> temp_celery.bat
echo echo. >> temp_celery.bat
echo echo Esperando 10 segundos para que el backend este listo... >> temp_celery.bat
echo timeout /t 10 /nobreak >> temp_celery.bat
echo echo. >> temp_celery.bat
echo echo Iniciando Celery Worker... >> temp_celery.bat
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2 >> temp_celery.bat
echo pause >> temp_celery.bat

REM Abrir las 3 terminales
echo Abriendo terminal Backend...
start "Backend" cmd /c temp_backend.bat

timeout /t 2 /nobreak >nul

echo Abriendo terminal Frontend...
start "Frontend" cmd /c temp_frontend.bat

timeout /t 2 /nobreak >nul

echo Abriendo terminal Celery Worker...
start "Celery" cmd /c temp_celery.bat

echo.
echo =====================================================
echo DESARROLLO INICIADO AUTOMATICAMENTE
echo =====================================================
echo.
echo Se han abierto 3 terminales:
echo  [1] Backend  - http://localhost:5175 (Flask + venv)
echo  [2] Frontend - http://localhost:5178 (React + Vite)
echo  [3] Celery   - Worker para conversiones (venv)
echo.
echo Redis esta corriendo en: localhost:6379
echo.
echo ACCEDER A LA APLICACION:
echo  -> http://localhost:5178
echo.
echo Para DETENER todo:
echo  1. Cierra las 3 terminales (Ctrl+C en cada una)
echo  2. Ejecuta: docker stop redis-anclora
echo.
echo Los archivos temporales se eliminaran automaticamente.
echo.

REM Limpiar archivos temporales después de 60 segundos
timeout /t 60 /nobreak >nul
del temp_backend.bat >nul 2>&1
del temp_frontend.bat >nul 2>&1
del temp_celery.bat >nul 2>&1

pause