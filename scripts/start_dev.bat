@echo off
title Anclora PDF2EPUB - INICIAR Desarrollo
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - INICIAR DESARROLLO
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

REM Detener contenedores anteriores (por si acaso)
echo Limpiando contenedores anteriores...
docker stop redis-anclora >nul 2>&1
docker rm redis-anclora >nul 2>&1

REM Iniciar Redis
echo Iniciando Redis en Docker...
docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes >nul

if %errorlevel% neq 0 (
    echo ERROR: No se pudo iniciar Redis
    pause
    exit /b 1
)

REM Esperar a que Redis este listo
echo Esperando que Redis este listo...
timeout /t 3 /nobreak >nul

REM Verificar Redis
docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Redis no responde
    pause
    exit /b 1
)
echo OK: Redis funcionando en puerto 6379

REM Preparar comandos para entorno virtual
if %USE_VENV%==1 (
    set VENV_CMD=call "%PROJECT_FOLDER%\venv-py311\Scripts\activate.bat"
) else (
    set VENV_CMD=echo [Sin entorno virtual - usando Python del sistema]
)

REM Crear scripts para cada terminal
echo Creando scripts para terminales...

REM Script Backend
echo @echo off > "%TEMP%\anclora_backend.bat"
echo title [ANCLORA] Backend Flask - Puerto 5175 >> "%TEMP%\anclora_backend.bat"
echo color 02 >> "%TEMP%\anclora_backend.bat"
echo echo ================================== >> "%TEMP%\anclora_backend.bat"
echo echo    BACKEND FLASK - Puerto 5175 >> "%TEMP%\anclora_backend.bat"
echo echo    Carpeta: %PROJECT_FOLDER% >> "%TEMP%\anclora_backend.bat"
echo echo ================================== >> "%TEMP%\anclora_backend.bat"
echo echo. >> "%TEMP%\anclora_backend.bat"
echo cd /d "%PROJECT_FOLDER%\backend" >> "%TEMP%\anclora_backend.bat"
echo %VENV_CMD% >> "%TEMP%\anclora_backend.bat"
echo echo Instalando dependencias Python... >> "%TEMP%\anclora_backend.bat"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.bat"
echo echo. >> "%TEMP%\anclora_backend.bat"
echo echo Iniciando servidor Flask... >> "%TEMP%\anclora_backend.bat"
echo python main.py >> "%TEMP%\anclora_backend.bat"
echo echo. >> "%TEMP%\anclora_backend.bat"
echo echo Backend detenido. >> "%TEMP%\anclora_backend.bat"
echo pause >> "%TEMP%\anclora_backend.bat"

REM Script Frontend
echo @echo off > "%TEMP%\anclora_frontend.bat"
echo title [ANCLORA] Frontend React - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo color 09 >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo echo   FRONTEND REACT - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo echo   Carpeta: %PROJECT_FOLDER%\frontend >> "%TEMP%\anclora_frontend.bat"
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

REM Script Celery
echo @echo off > "%TEMP%\anclora_celery.bat"
echo title [ANCLORA] Celery Worker - Conversiones >> "%TEMP%\anclora_celery.bat"
echo color 05 >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo  CELERY WORKER - Conversiones PDF >> "%TEMP%\anclora_celery.bat"
echo echo  Carpeta: %PROJECT_FOLDER%\backend >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo cd /d "%PROJECT_FOLDER%\backend" >> "%TEMP%\anclora_celery.bat"
echo %VENV_CMD% >> "%TEMP%\anclora_celery.bat"
echo echo Esperando 15 segundos a que el backend este listo... >> "%TEMP%\anclora_celery.bat"
echo timeout /t 15 /nobreak >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo echo Iniciando Celery Worker... >> "%TEMP%\anclora_celery.bat"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2 >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo echo Celery Worker detenido. >> "%TEMP%\anclora_celery.bat"
echo pause >> "%TEMP%\anclora_celery.bat"

echo.
echo =====================================================
echo ABRIENDO 3 TERMINALES...
echo =====================================================
echo.

REM Abrir terminales con un poco de delay entre cada uno
echo [1/3] Abriendo Backend...
start "Backend" "%TEMP%\anclora_backend.bat"

timeout /t 2 /nobreak >nul

echo [2/3] Abriendo Frontend...
start "Frontend" "%TEMP%\anclora_frontend.bat"

timeout /t 2 /nobreak >nul

echo [3/3] Abriendo Celery Worker...
start "Celery" "%TEMP%\anclora_celery.bat"

echo.
echo =====================================================
echo DESARROLLO INICIADO CORRECTAMENTE
echo =====================================================
echo.
echo Ubicacion: %PROJECT_FOLDER%
echo.
echo Servicios iniciados:
echo  [Backend]  Flask en puerto 5175
echo  [Frontend] React en puerto 5178
echo  [Worker]   Celery para conversiones
echo  [Redis]    Base de datos en puerto 6379
echo.
echo ACCEDE A TU APLICACION:
echo  --^> http://localhost:5178
echo.
echo Para DETENER todo ejecuta: stop_dev.bat
echo.

timeout /t 5 /nobreak >nul
pause