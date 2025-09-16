@echo off
setlocal EnableDelayedExpansion
title Anclora PDF2EPUB - INICIAR (Corregido)
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - INICIAR DESARROLLO
echo =====================================================
echo.

REM Obtener carpeta padre del script (salir de scripts/ al repo)
for %%i in ("%~dp0..") do set "REPO_ROOT=%%~fi"

echo Carpeta actual del repositorio detectada:
echo !REPO_ROOT!
echo.
echo Opciones:
echo [1] Usar esta carpeta
echo [2] Seleccionar otra carpeta
echo.
set /p FOLDER_CHOICE=Elige una opcion (1-2):

if "!FOLDER_CHOICE!"=="1" (
    set "PROJECT_FOLDER=!REPO_ROOT!"
    echo.
    echo Usando carpeta actual del repositorio.
) else if "!FOLDER_CHOICE!"=="2" (
    echo.
    echo Abriendo selector de carpetas...

    REM Crear script PowerShell para selector de carpeta
    (
        echo Add-Type -AssemblyName System.Windows.Forms
        echo $folder = New-Object System.Windows.Forms.FolderBrowserDialog
        echo $folder.Description = "Selecciona la carpeta del proyecto Anclora PDF2EPUB"
        echo $folder.ShowNewFolderButton = $false
        echo $folder.SelectedPath = "!REPO_ROOT!"
        echo $result = $folder.ShowDialog^(^)
        echo if ^($result -eq [System.Windows.Forms.DialogResult]::OK^) {
        echo     Write-Output $folder.SelectedPath
        echo } else {
        echo     Write-Output "CANCELLED"
        echo }
    ) > "%TEMP%\selectfolder.ps1"

    for /f "delims=" %%i in ('powershell -ExecutionPolicy Bypass -File "%TEMP%\selectfolder.ps1"') do set "PROJECT_FOLDER=%%i"
    del "%TEMP%\selectfolder.ps1" >nul 2>&1

    if "!PROJECT_FOLDER!"=="CANCELLED" (
        echo Seleccion cancelada. Saliendo...
        pause
        exit /b 1
    )

    echo.
    echo Carpeta seleccionada: !PROJECT_FOLDER!
) else (
    echo Opcion invalida. Usando carpeta actual.
    set "PROJECT_FOLDER=!REPO_ROOT!"
)

echo.
echo =====================================================
echo VERIFICANDO ESTRUCTURA DEL PROYECTO...
echo =====================================================

REM Verificar estructura del proyecto
if not exist "!PROJECT_FOLDER!\backend" (
    echo.
    echo ERROR: No se encontro la carpeta 'backend' en:
    echo !PROJECT_FOLDER!
    echo.
    echo La estructura debe ser:
    echo   carpeta-proyecto/
    echo   ├── backend/
    echo   ├── frontend/
    echo   └── venv-py311/ ^(opcional^)
    echo.
    pause
    exit /b 1
)

if not exist "!PROJECT_FOLDER!\frontend" (
    echo.
    echo ERROR: No se encontro la carpeta 'frontend' en:
    echo !PROJECT_FOLDER!
    echo.
    echo La estructura debe ser:
    echo   carpeta-proyecto/
    echo   ├── backend/
    echo   ├── frontend/
    echo   └── venv-py311/ ^(opcional^)
    echo.
    pause
    exit /b 1
)

echo OK: Estructura del proyecto verificada

REM Verificar entorno virtual
set "USE_VENV=0"
if exist "!PROJECT_FOLDER!\venv-py311\Scripts\activate.bat" (
    echo OK: Entorno virtual encontrado
    set "USE_VENV=1"
) else (
    echo AVISO: No se encontro entorno virtual venv-py311
    echo        Se usara Python del sistema
)

REM Verificar Docker
echo.
echo Verificando Docker...
docker version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ERROR: Docker no esta corriendo.
    echo.
    echo Solucion:
    echo 1. Abre Docker Desktop
    echo 2. Espera a que este completamente iniciado
    echo 3. Vuelve a ejecutar este script
    echo.
    pause
    exit /b 1
)
echo OK: Docker listo

echo.
echo =====================================================
echo SELECCIONAR TIPO DE TERMINAL
echo =====================================================
echo.
echo Que tipo de terminal quieres usar para los 3 servicios?
echo.
echo [1] CMD        - Command Prompt ^(mas compatible^)
echo [2] PowerShell - Windows PowerShell ^(recomendado^)
echo [3] Git Bash   - Bash en Windows ^(requiere Git^)
echo.
set /p TERMINAL_CHOICE=Elige una opcion (1-3):

if "!TERMINAL_CHOICE!"=="1" (
    set "TERMINAL_TYPE=cmd"
    echo.
    echo Seleccionado: Command Prompt
) else if "!TERMINAL_CHOICE!"=="2" (
    set "TERMINAL_TYPE=powershell"
    echo.
    echo Seleccionado: PowerShell
) else if "!TERMINAL_CHOICE!"=="3" (
    set "TERMINAL_TYPE=bash"
    echo.
    echo Seleccionado: Git Bash
    REM Verificar si bash esta disponible
    where bash >nul 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo AVISO: Git Bash no encontrado.
        echo Se cambiara a PowerShell como alternativa.
        set "TERMINAL_TYPE=powershell"
    )
) else (
    echo.
    echo Opcion invalida. Usando PowerShell por defecto.
    set "TERMINAL_TYPE=powershell"
)

echo.
echo =====================================================
echo CONFIGURANDO SERVICIOS...
echo =====================================================

REM Detener contenedores anteriores
echo [1/3] Limpiando contenedores Redis anteriores...
docker stop redis-anclora >nul 2>&1
docker rm redis-anclora >nul 2>&1

REM Iniciar Redis
echo [2/3] Iniciando Redis en Docker...
docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes >nul

if !errorlevel! neq 0 (
    echo.
    echo ERROR: No se pudo iniciar Redis
    echo.
    echo Posibles causas:
    echo - Puerto 6379 ocupado
    echo - Docker sin permisos
    echo - Imagen redis no disponible
    echo.
    pause
    exit /b 1
)

REM Esperar y verificar Redis
echo [3/3] Verificando Redis...
timeout /t 3 /nobreak >nul

docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Redis no responde correctamente
    pause
    exit /b 1
)
echo OK: Redis funcionando en puerto 6379

echo.
echo =====================================================
echo CREANDO SCRIPTS PARA !TERMINAL_TYPE!...
echo =====================================================

REM Preparar comandos para venv
if "!USE_VENV!"=="1" (
    set "VENV_ACTIVATE_CMD=call "!PROJECT_FOLDER!\venv-py311\Scripts\activate.bat""
    set "VENV_ACTIVATE_PS=& '!PROJECT_FOLDER!\venv-py311\Scripts\Activate.ps1'"
    set "VENV_ACTIVATE_BASH=source '!PROJECT_FOLDER!/venv-py311/Scripts/activate'"
) else (
    set "VENV_ACTIVATE_CMD=echo [Usando Python del sistema]"
    set "VENV_ACTIVATE_PS=Write-Host '[Usando Python del sistema]' -ForegroundColor Yellow"
    set "VENV_ACTIVATE_BASH=echo '[Usando Python del sistema]'"
)

REM Crear scripts segun terminal elegido
if "!TERMINAL_TYPE!"=="cmd" (
    call :create_cmd_scripts
) else if "!TERMINAL_TYPE!"=="powershell" (
    call :create_powershell_scripts
) else if "!TERMINAL_TYPE!"=="bash" (
    call :create_bash_scripts
)

REM Abrir terminales
echo.
echo Abriendo 3 terminales tipo !TERMINAL_TYPE!...

if "!TERMINAL_TYPE!"=="cmd" (
    start "Backend - Flask" cmd /c "%TEMP%\anclora_backend.bat"
    timeout /t 2 /nobreak >nul
    start "Frontend - React" cmd /c "%TEMP%\anclora_frontend.bat"
    timeout /t 2 /nobreak >nul
    start "Celery - Worker" cmd /c "%TEMP%\anclora_celery.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    REM Verificar Windows Terminal
    where wt >nul 2>&1
    if !errorlevel!==0 (
        echo Usando Windows Terminal...
        start "" wt new-tab --title "Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_backend.ps1"
        timeout /t 1 /nobreak >nul
        start "" wt new-tab --title "Frontend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_frontend.ps1"
        timeout /t 1 /nobreak >nul
        start "" wt new-tab --title "Celery" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_celery.ps1"
    ) else (
        echo Usando ventanas PowerShell separadas...
        start "Backend - Flask" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_backend.ps1"
        timeout /t 2 /nobreak >nul
        start "Frontend - React" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_frontend.ps1"
        timeout /t 2 /nobreak >nul
        start "Celery - Worker" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_celery.ps1"
    )
) else if "!TERMINAL_TYPE!"=="bash" (
    start "Backend - Flask" bash "%TEMP%\anclora_backend.sh"
    timeout /t 2 /nobreak >nul
    start "Frontend - React" bash "%TEMP%\anclora_frontend.sh"
    timeout /t 2 /nobreak >nul
    start "Celery - Worker" bash "%TEMP%\anclora_celery.sh"
)

echo.
echo =====================================================
echo DESARROLLO INICIADO CORRECTAMENTE
echo =====================================================
echo.
echo Configuracion:
echo   Carpeta:   !PROJECT_FOLDER!
echo   Terminal:  !TERMINAL_TYPE!
echo   Venv:      !USE_VENV! ^(1=si, 0=no^)
echo.
echo Servicios activos:
echo   Backend   - http://localhost:5175 ^(Flask API^)
echo   Frontend  - http://localhost:5178 ^(React App^)
echo   Celery    - Worker para conversiones
echo   Redis     - Base de datos puerto 6379
echo.
echo ACCEDE A TU APLICACION:
echo   ==^> http://localhost:5178
echo.
echo Para DETENER todo: stop_dev.bat
echo.

timeout /t 5 /nobreak >nul
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
exit /b 0

REM ============ FUNCIONES PARA CREAR SCRIPTS ============

:create_cmd_scripts
REM Backend CMD
(
    echo @echo off
    echo title Backend Flask - Puerto 5175
    echo color 02
    echo echo ==================================
    echo echo   BACKEND FLASK - Puerto 5175
    echo echo   Carpeta: !PROJECT_FOLDER!
    echo echo ==================================
    echo echo.
    echo cd /d "!PROJECT_FOLDER!"
    echo !VENV_ACTIVATE_CMD!
    echo cd backend
    echo echo Instalando dependencias...
    echo pip install -r requirements.txt
    echo echo.
    echo echo Iniciando Flask...
    echo python main.py
    echo pause
) > "%TEMP%\anclora_backend.bat"

REM Frontend CMD
(
    echo @echo off
    echo title Frontend React - Puerto 5178
    echo color 09
    echo echo ==================================
    echo echo  FRONTEND REACT - Puerto 5178
    echo echo  Carpeta: !PROJECT_FOLDER!\frontend
    echo echo ==================================
    echo echo.
    echo cd /d "!PROJECT_FOLDER!\frontend"
    echo echo Instalando dependencias...
    echo npm install
    echo echo.
    echo echo Iniciando Vite...
    echo npm start
    echo pause
) > "%TEMP%\anclora_frontend.bat"

REM Celery CMD
(
    echo @echo off
    echo title Celery Worker
    echo color 05
    echo echo ==================================
    echo echo  CELERY WORKER - Conversiones
    echo echo  Carpeta: !PROJECT_FOLDER!\backend
    echo echo ==================================
    echo echo.
    echo cd /d "!PROJECT_FOLDER!"
    echo !VENV_ACTIVATE_CMD!
    echo cd backend
    echo echo Esperando 15 segundos a que Flask este listo...
    echo timeout /t 15 /nobreak
    echo echo.
    echo echo Iniciando Celery Worker...
    echo "C:\Users\Usuario\Workspace\01_Proyectos\Anclora-PDF2EPUB-Claude\venv-py311\Scripts\celery.exe" -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
    echo pause
) > "%TEMP%\anclora_celery.bat"
goto :eof

:create_powershell_scripts
REM Backend PowerShell
(
    echo Write-Host '==================================' -ForegroundColor Green
    echo Write-Host '  BACKEND FLASK - Puerto 5175' -ForegroundColor Green
    echo Write-Host '  Carpeta: !PROJECT_FOLDER!' -ForegroundColor Gray
    echo Write-Host '==================================' -ForegroundColor Green
    echo Write-Host ''
    echo Set-Location '!PROJECT_FOLDER!'
    echo !VENV_ACTIVATE_PS!
    echo Set-Location backend
    echo Write-Host 'Instalando dependencias...' -ForegroundColor Yellow
    echo pip install -r requirements.txt
    echo Write-Host 'Iniciando Flask...' -ForegroundColor Yellow
    echo python main.py
) > "%TEMP%\anclora_backend.ps1"

REM Frontend PowerShell
(
    echo Write-Host '==================================' -ForegroundColor Blue
    echo Write-Host ' FRONTEND REACT - Puerto 5178' -ForegroundColor Blue
    echo Write-Host ' Carpeta: !PROJECT_FOLDER!\frontend' -ForegroundColor Gray
    echo Write-Host '==================================' -ForegroundColor Blue
    echo Write-Host ''
    echo Set-Location '!PROJECT_FOLDER!\frontend'
    echo Write-Host 'Instalando dependencias...' -ForegroundColor Yellow
    echo npm install
    echo Write-Host 'Iniciando Vite...' -ForegroundColor Yellow
    echo npm start
) > "%TEMP%\anclora_frontend.ps1"

REM Celery PowerShell
(
    echo Write-Host '==================================' -ForegroundColor Magenta
    echo Write-Host ' CELERY WORKER - Conversiones' -ForegroundColor Magenta
    echo Write-Host ' Carpeta: !PROJECT_FOLDER!\backend' -ForegroundColor Gray
    echo Write-Host '==================================' -ForegroundColor Magenta
    echo Write-Host ''
    echo Set-Location '!PROJECT_FOLDER!'
    echo !VENV_ACTIVATE_PS!
    echo Set-Location backend
    echo Write-Host 'Esperando 15 segundos...' -ForegroundColor Yellow
    echo Start-Sleep -Seconds 15
    echo Write-Host 'Iniciando Celery Worker...' -ForegroundColor Yellow
    echo ^& 'C:\Users\Usuario\Workspace\01_Proyectos\Anclora-PDF2EPUB-Claude\venv-py311\Scripts\celery.exe' -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
) > "%TEMP%\anclora_celery.ps1"
goto :eof

:create_bash_scripts
REM Backend Bash
(
    echo #!/bin/bash
    echo echo '=================================='
    echo echo '  BACKEND FLASK - Puerto 5175'
    echo echo '  Carpeta: !PROJECT_FOLDER!'
    echo echo '=================================='
    echo echo ''
    echo cd '!PROJECT_FOLDER!'
    echo !VENV_ACTIVATE_BASH!
    echo cd backend
    echo echo 'Instalando dependencias...'
    echo pip install -r requirements.txt
    echo echo 'Iniciando Flask...'
    echo python main.py
    echo read -p 'Presiona Enter para cerrar'
) > "%TEMP%\anclora_backend.sh"

REM Frontend Bash
(
    echo #!/bin/bash
    echo echo '=================================='
    echo echo ' FRONTEND REACT - Puerto 5178'
    echo echo ' Carpeta: !PROJECT_FOLDER!/frontend'
    echo echo '=================================='
    echo echo ''
    echo cd '!PROJECT_FOLDER!/frontend'
    echo echo 'Instalando dependencias...'
    echo npm install
    echo echo 'Iniciando Vite...'
    echo npm start
    echo read -p 'Presiona Enter para cerrar'
) > "%TEMP%\anclora_frontend.sh"

REM Celery Bash
(
    echo #!/bin/bash
    echo echo '=================================='
    echo echo ' CELERY WORKER - Conversiones'
    echo echo ' Carpeta: !PROJECT_FOLDER!/backend'
    echo echo '=================================='
    echo echo ''
    echo cd '!PROJECT_FOLDER!'
    echo !VENV_ACTIVATE_BASH!
    echo cd backend
    echo echo 'Esperando 15 segundos...'
    echo sleep 15
    echo echo 'Iniciando Celery Worker...'
    echo 'C:\Users\Usuario\Workspace\01_Proyectos\Anclora-PDF2EPUB-Claude\venv-py311\Scripts\celery.exe' -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
    echo read -p 'Presiona Enter para cerrar'
) > "%TEMP%\anclora_celery.sh"
goto :eof