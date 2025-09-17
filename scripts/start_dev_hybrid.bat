@echo off
title Anclora PDF2EPUB - INICIAR Desarrollo Híbrido
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - DESARROLLO HÍBRIDO
echo =====================================================
echo Backend + Redis: Docker
echo Frontend + Celery: Local
echo =====================================================
echo.

REM Usar la carpeta padre del script (que está en scripts/)
for %%i in ("%~dp0..") do set PROJECT_FOLDER=%%~fi

echo Carpeta del proyecto: %PROJECT_FOLDER%

REM Verificar estructura del proyecto
if not exist "%PROJECT_FOLDER%\backend" (
    echo ERROR: No se encontro la carpeta 'backend'
    pause
    exit /b 1
)

if not exist "%PROJECT_FOLDER%\frontend" (
    echo ERROR: No se encontro la carpeta 'frontend'
    pause
    exit /b 1
)

REM Verificar entorno virtual
set USE_VENV=0
if exist "%PROJECT_FOLDER%\venv-py311\Scripts\activate.bat" (
    echo OK: Entorno virtual encontrado
    set USE_VENV=1
) else (
    echo AVISO: No se encontro entorno virtual
)

REM Verificar Docker
echo Verificando Docker...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no esta corriendo. Inicia Docker Desktop primero.
    pause
    exit /b 1
)
echo OK: Docker listo

REM Verificar que Backend y Redis estén ejecutándose en Docker
echo Verificando servicios Docker...
docker ps | findstr "anclora-pdf2epub-claude-backend" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Backend no está ejecutándose en Docker.
    echo Por favor ejecuta: docker-compose -f docker-compose.dev.yml up backend redis -d
    pause
    exit /b 1
)

docker ps | findstr "anclora-pdf2epub-claude-redis" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Redis no está ejecutándose en Docker.
    echo Por favor ejecuta: docker-compose -f docker-compose.dev.yml up backend redis -d
    pause
    exit /b 1
)

echo OK: Backend y Redis ejecutándose en Docker

REM Preparar comandos para entorno virtual
if %USE_VENV%==1 (
    set VENV_CMD=call "%PROJECT_FOLDER%\venv-py311\Scripts\activate.bat"
) else (
    set VENV_CMD=echo [Sin entorno virtual - usando Python del sistema]
)

REM Crear scripts para cada terminal
echo Creando scripts para terminales...

REM Script Frontend Local
echo @echo off > "%TEMP%\anclora_frontend.bat"
echo title [ANCLORA] Frontend React - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo color 09 >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo echo   FRONTEND REACT LOCAL - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo echo   Carpeta: %PROJECT_FOLDER%\frontend >> "%TEMP%\anclora_frontend.bat"
echo echo   Backend: Docker puerto 5175 >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo echo. >> "%TEMP%\anclora_frontend.bat"
echo cd /d "%PROJECT_FOLDER%\frontend" >> "%TEMP%\anclora_frontend.bat"
echo echo Verificando si node_modules existe... >> "%TEMP%\anclora_frontend.bat"
echo if not exist "node_modules" ( >> "%TEMP%\anclora_frontend.bat"
echo     echo Instalando dependencias... >> "%TEMP%\anclora_frontend.bat"
echo     npm install --silent >> "%TEMP%\anclora_frontend.bat"
echo ^) else ( >> "%TEMP%\anclora_frontend.bat"
echo     echo Dependencias ya instaladas, omitiendo npm install >> "%TEMP%\anclora_frontend.bat"
echo ^) >> "%TEMP%\anclora_frontend.bat"
echo echo. >> "%TEMP%\anclora_frontend.bat"
echo echo Iniciando servidor Vite... >> "%TEMP%\anclora_frontend.bat"
echo npm start >> "%TEMP%\anclora_frontend.bat"
echo echo. >> "%TEMP%\anclora_frontend.bat"
echo echo Frontend detenido. >> "%TEMP%\anclora_frontend.bat"
echo pause >> "%TEMP%\anclora_frontend.bat"

REM Script Celery Local
echo @echo off > "%TEMP%\anclora_celery.bat"
echo title [ANCLORA] Celery Worker Local - Conversiones >> "%TEMP%\anclora_celery.bat"
echo color 05 >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo  CELERY WORKER LOCAL - Conversiones PDF >> "%TEMP%\anclora_celery.bat"
echo echo  Carpeta: %PROJECT_FOLDER%\backend >> "%TEMP%\anclora_celery.bat"
echo echo  Redis: Docker puerto 6379 >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo cd /d "%PROJECT_FOLDER%\backend" >> "%TEMP%\anclora_celery.bat"
echo %VENV_CMD% >> "%TEMP%\anclora_celery.bat"
echo echo Esperando 10 segundos a que los servicios estén listos... >> "%TEMP%\anclora_celery.bat"
echo timeout /t 10 /nobreak >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo echo Instalando dependencias si es necesario... >> "%TEMP%\anclora_celery.bat"
echo pip install -r requirements.txt >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo echo Iniciando Celery Worker... >> "%TEMP%\anclora_celery.bat"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2 >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo echo Celery Worker detenido. >> "%TEMP%\anclora_celery.bat"
echo pause >> "%TEMP%\anclora_celery.bat"

echo.
echo =====================================================
echo ABRIENDO 2 TERMINALES...
echo =====================================================
echo.

REM Abrir terminales con un poco de delay entre cada uno
echo [1/2] Abriendo Frontend Local...
start "Frontend Local" "%TEMP%\anclora_frontend.bat"

timeout /t 3 /nobreak >nul

echo [2/2] Abriendo Celery Worker Local...
start "Celery Local" "%TEMP%\anclora_celery.bat"

echo.
echo =====================================================
echo DESARROLLO HÍBRIDO INICIADO CORRECTAMENTE
echo =====================================================
echo.
echo Ubicacion: %PROJECT_FOLDER%
echo.
echo Servicios iniciados:
echo  [Backend]  Flask en Docker puerto 5175
echo  [Redis]    Docker puerto 6379
echo  [Frontend] React LOCAL puerto 5178
echo  [Worker]   Celery LOCAL para conversiones
echo.
echo ACCEDE A TU APLICACION:
echo  --^> http://localhost:5178
echo.
echo Para DETENER servicios Docker ejecuta:
echo  docker-compose -f docker-compose.dev.yml stop
echo.

timeout /t 5 /nobreak >nul
pause