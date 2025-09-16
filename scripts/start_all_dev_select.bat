@echo off
title Anclora PDF2EPUB - Selector de Carpeta
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - SELECCIONAR CARPETA DEL PROYECTO
echo =====================================================
echo.

REM Crear script VBS para seleccionar carpeta
echo Set objShell = CreateObject("Shell.Application") > "%TEMP%\selectfolder.vbs"
echo Set objFolder = objShell.BrowseForFolder(0, "Selecciona la carpeta del proyecto Anclora PDF2EPUB", 0, "%CD%") >> "%TEMP%\selectfolder.vbs"
echo If Not objFolder Is Nothing Then >> "%TEMP%\selectfolder.vbs"
echo     WScript.Echo objFolder.Self.Path >> "%TEMP%\selectfolder.vbs"
echo End If >> "%TEMP%\selectfolder.vbs"

REM Ejecutar selector y obtener carpeta
for /f "delims=" %%i in ('cscript //nologo "%TEMP%\selectfolder.vbs"') do set PROJECT_FOLDER=%%i

REM Limpiar archivo temporal
del "%TEMP%\selectfolder.vbs" >nul 2>&1

REM Verificar si se selecciono carpeta
if "%PROJECT_FOLDER%"=="" (
    echo No se selecciono ninguna carpeta. Saliendo...
    pause
    exit /b 1
)

echo Carpeta seleccionada: %PROJECT_FOLDER%

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
    echo ERROR: Docker no esta corriendo
    pause
    exit /b 1
)
echo OK: Docker listo

REM Configurar Redis
echo Configurando Redis...
docker stop redis-anclora >nul 2>&1
docker rm redis-anclora >nul 2>&1

docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes >nul

timeout /t 3 /nobreak >nul
echo OK: Redis listo en puerto 6379

REM Crear scripts para terminales
if %USE_VENV%==1 (
    set VENV_CMD=call "%PROJECT_FOLDER%\venv-py311\Scripts\activate.bat"
) else (
    set VENV_CMD=echo Sin entorno virtual
)

REM Script Backend
echo @echo off > "%TEMP%\backend.bat"
echo title Backend - Flask >> "%TEMP%\backend.bat"
echo cd /d "%PROJECT_FOLDER%" >> "%TEMP%\backend.bat"
echo %VENV_CMD% >> "%TEMP%\backend.bat"
echo cd backend >> "%TEMP%\backend.bat"
echo echo BACKEND - Instalando dependencias... >> "%TEMP%\backend.bat"
echo pip install -r requirements.txt >> "%TEMP%\backend.bat"
echo echo BACKEND - Iniciando Flask... >> "%TEMP%\backend.bat"
echo python main.py >> "%TEMP%\backend.bat"
echo pause >> "%TEMP%\backend.bat"

REM Script Frontend
echo @echo off > "%TEMP%\frontend.bat"
echo title Frontend - React >> "%TEMP%\frontend.bat"
echo cd /d "%PROJECT_FOLDER%\frontend" >> "%TEMP%\frontend.bat"
echo echo FRONTEND - Instalando dependencias... >> "%TEMP%\frontend.bat"
echo npm install >> "%TEMP%\frontend.bat"
echo echo FRONTEND - Iniciando Vite... >> "%TEMP%\frontend.bat"
echo npm start >> "%TEMP%\frontend.bat"
echo pause >> "%TEMP%\frontend.bat"

REM Script Celery
echo @echo off > "%TEMP%\celery.bat"
echo title Celery - Worker >> "%TEMP%\celery.bat"
echo cd /d "%PROJECT_FOLDER%" >> "%TEMP%\celery.bat"
echo %VENV_CMD% >> "%TEMP%\celery.bat"
echo cd backend >> "%TEMP%\celery.bat"
echo echo Esperando 15 segundos para que el backend este listo... >> "%TEMP%\celery.bat"
echo timeout /t 15 /nobreak >> "%TEMP%\celery.bat"
echo echo CELERY - Iniciando Worker... >> "%TEMP%\celery.bat"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet >> "%TEMP%\celery.bat"
echo pause >> "%TEMP%\celery.bat"

echo.
echo Abriendo 3 terminales en: %PROJECT_FOLDER%

REM Abrir terminales
start "Backend" cmd /c "%TEMP%\backend.bat"
timeout /t 1 /nobreak >nul
start "Frontend" cmd /c "%TEMP%\frontend.bat"
timeout /t 1 /nobreak >nul
start "Celery" cmd /c "%TEMP%\celery.bat"

echo.
echo =====================================================
echo TERMINALES ABIERTOS EN: %PROJECT_FOLDER%
echo =====================================================
echo.
echo URLs:
echo   Frontend: http://localhost:5178
echo   Backend:  http://localhost:5175
echo   Redis:    localhost:6379
echo.

pause