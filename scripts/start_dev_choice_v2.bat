@echo off
title Anclora PDF2EPUB - INICIAR con Selector Mejorado
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - INICIAR DESARROLLO
echo =====================================================
echo.

REM Obtener carpeta padre del script (salir de scripts/ al repo)
for %%i in ("%~dp0..") do set "REPO_ROOT=%%~fi"

echo Carpeta actual del repositorio detectada: %REPO_ROOT%
echo.
echo Opciones:
echo [1] Usar esta carpeta: %REPO_ROOT%
echo [2] Seleccionar otra carpeta
echo.
set /p FOLDER_CHOICE=Elige una opcion (1-2):

if "%FOLDER_CHOICE%"=="1" (
    set "PROJECT_FOLDER=%REPO_ROOT%"
    echo Usando carpeta actual del repositorio.
) else if "%FOLDER_CHOICE%"=="2" (
    echo Abriendo selector de carpetas...

    REM Crear script PowerShell para selector de carpeta (mas robusto)
    echo Add-Type -AssemblyName System.Windows.Forms > "%TEMP%\selectfolder.ps1"
    echo $folder = New-Object System.Windows.Forms.FolderBrowserDialog >> "%TEMP%\selectfolder.ps1"
    echo $folder.Description = "Selecciona la carpeta del proyecto Anclora PDF2EPUB" >> "%TEMP%\selectfolder.ps1"
    echo $folder.ShowNewFolderButton = $false >> "%TEMP%\selectfolder.ps1"
    echo $folder.SelectedPath = "%REPO_ROOT%" >> "%TEMP%\selectfolder.ps1"
    echo $result = $folder.ShowDialog() >> "%TEMP%\selectfolder.ps1"
    echo if ($result -eq [System.Windows.Forms.DialogResult]::OK) { >> "%TEMP%\selectfolder.ps1"
    echo     Write-Output $folder.SelectedPath >> "%TEMP%\selectfolder.ps1"
    echo } else { >> "%TEMP%\selectfolder.ps1"
    echo     Write-Output "CANCELLED" >> "%TEMP%\selectfolder.ps1"
    echo } >> "%TEMP%\selectfolder.ps1"

    for /f "delims=" %%i in ('powershell -ExecutionPolicy Bypass -File "%TEMP%\selectfolder.ps1"') do set PROJECT_FOLDER=%%i
    del "%TEMP%\selectfolder.ps1" >nul 2>&1

    if "!PROJECT_FOLDER!"=="CANCELLED" (
        echo Seleccion cancelada. Saliendo...
        pause
        exit /b 1
    )

    echo Carpeta seleccionada: !PROJECT_FOLDER!
) else (
    echo Opcion invalida. Usando carpeta actual.
    set "PROJECT_FOLDER=%REPO_ROOT%"
)

REM Habilitar expansion de variables retardada
setlocal EnableDelayedExpansion

echo.
echo Carpeta final: !PROJECT_FOLDER!

REM Verificar estructura del proyecto
if not exist "!PROJECT_FOLDER!\backend" (
    echo ERROR: No se encontro la carpeta 'backend' en: !PROJECT_FOLDER!
    echo.
    echo La estructura debe ser:
    echo   carpeta-proyecto/
    echo   ├── backend/
    echo   ├── frontend/
    echo   └── venv-py311/ (opcional)
    echo.
    pause
    exit /b 1
)

if not exist "!PROJECT_FOLDER!\frontend" (
    echo ERROR: No se encontro la carpeta 'frontend' en: !PROJECT_FOLDER!
    echo.
    echo La estructura debe ser:
    echo   carpeta-proyecto/
    echo   ├── backend/
    echo   ├── frontend/
    echo   └── venv-py311/ (opcional)
    echo.
    pause
    exit /b 1
)

REM Verificar entorno virtual
set USE_VENV=0
if exist "!PROJECT_FOLDER!\venv-py311\Scripts\activate.bat" (
    echo OK: Entorno virtual encontrado
    set USE_VENV=1
) else (
    echo AVISO: No se encontro entorno virtual venv-py311
    echo        Se usara Python del sistema
)

REM Verificar Docker
echo.
echo Verificando Docker...
docker version >nul 2>&1
if !errorlevel! neq 0 (
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
echo [1] CMD        - Command Prompt (mas compatible)
echo [2] PowerShell - Windows PowerShell (recomendado)
echo [3] Git Bash   - Bash en Windows (requiere Git)
echo.
set /p TERMINAL_CHOICE=Elige una opcion (1-3):

if "!TERMINAL_CHOICE!"=="1" (
    set TERMINAL_TYPE=cmd
    echo Seleccionado: Command Prompt
) else if "!TERMINAL_CHOICE!"=="2" (
    set TERMINAL_TYPE=powershell
    echo Seleccionado: PowerShell
) else if "!TERMINAL_CHOICE!"=="3" (
    set TERMINAL_TYPE=bash
    echo Seleccionado: Git Bash
    REM Verificar si bash esta disponible
    where bash >nul 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo AVISO: Git Bash no encontrado.
        echo Se cambiara a PowerShell como alternativa.
        set TERMINAL_TYPE=powershell
    )
) else (
    echo Opcion invalida. Usando PowerShell por defecto.
    set TERMINAL_TYPE=powershell
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

REM Preparar scripts segun terminal
if "!TERMINAL_TYPE!"=="cmd" (
    call :create_cmd_scripts
    call :launch_cmd_terminals
) else if "!TERMINAL_TYPE!"=="powershell" (
    call :create_powershell_scripts
    call :launch_powershell_terminals
) else if "!TERMINAL_TYPE!"=="bash" (
    call :create_bash_scripts
    call :launch_bash_terminals
)

echo.
echo =====================================================
echo DESARROLLO INICIADO CORRECTAMENTE
echo =====================================================
echo.
echo Configuracion:
echo   Carpeta:   !PROJECT_FOLDER!
echo   Terminal:  !TERMINAL_TYPE!
echo   Venv:      !USE_VENV! (1=si, 0=no)
echo.
echo Servicios activos:
echo   Backend   - http://localhost:5175 (Flask API)
echo   Frontend  - http://localhost:5178 (React App)
echo   Celery    - Worker para conversiones
echo   Redis     - Base de datos puerto 6379
echo.
echo ACCEDE A TU APLICACION:
echo   ==^> http://localhost:5178
echo.
echo Para DETENER todo: stop_dev.bat
echo.

timeout /t 5 /nobreak >nul
pause
exit /b 0

REM ============ FUNCIONES ============

:create_cmd_scripts
if !USE_VENV!==1 (
    set VENV_CMD=call "!PROJECT_FOLDER!\venv-py311\Scripts\activate.bat"
) else (
    set VENV_CMD=echo [Usando Python del sistema]
)

REM Backend CMD
echo @echo off > "%TEMP%\anclora_backend.bat"
echo title Backend Flask - Puerto 5175 >> "%TEMP%\anclora_backend.bat"
echo color 02 >> "%TEMP%\anclora_backend.bat"
echo echo ================================== >> "%TEMP%\anclora_backend.bat"
echo echo   BACKEND FLASK - Puerto 5175 >> "%TEMP%\anclora_backend.bat"
echo echo   Carpeta: !PROJECT_FOLDER! >> "%TEMP%\anclora_backend.bat"
echo echo ================================== >> "%TEMP%\anclora_backend.bat"
echo echo. >> "%TEMP%\anclora_backend.bat"
echo cd /d "!PROJECT_FOLDER!" >> "%TEMP%\anclora_backend.bat"
echo !VENV_CMD! >> "%TEMP%\anclora_backend.bat"
echo cd backend >> "%TEMP%\anclora_backend.bat"
echo echo Instalando dependencias... >> "%TEMP%\anclora_backend.bat"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.bat"
echo echo. >> "%TEMP%\anclora_backend.bat"
echo echo Iniciando Flask... >> "%TEMP%\anclora_backend.bat"
echo python main.py >> "%TEMP%\anclora_backend.bat"
echo pause >> "%TEMP%\anclora_backend.bat"

REM Frontend CMD
echo @echo off > "%TEMP%\anclora_frontend.bat"
echo title Frontend React - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo color 09 >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo echo  FRONTEND REACT - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo echo  Carpeta: !PROJECT_FOLDER!\frontend >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo echo. >> "%TEMP%\anclora_frontend.bat"
echo cd /d "!PROJECT_FOLDER!\frontend" >> "%TEMP%\anclora_frontend.bat"
echo echo Instalando dependencias... >> "%TEMP%\anclora_frontend.bat"
echo npm install >> "%TEMP%\anclora_frontend.bat"
echo echo. >> "%TEMP%\anclora_frontend.bat"
echo echo Iniciando Vite... >> "%TEMP%\anclora_frontend.bat"
echo npm start >> "%TEMP%\anclora_frontend.bat"
echo pause >> "%TEMP%\anclora_frontend.bat"

REM Celery CMD
echo @echo off > "%TEMP%\anclora_celery.bat"
echo title Celery Worker >> "%TEMP%\anclora_celery.bat"
echo color 05 >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo  CELERY WORKER - Conversiones >> "%TEMP%\anclora_celery.bat"
echo echo  Carpeta: !PROJECT_FOLDER!\backend >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo cd /d "!PROJECT_FOLDER!" >> "%TEMP%\anclora_celery.bat"
echo !VENV_CMD! >> "%TEMP%\anclora_celery.bat"
echo cd backend >> "%TEMP%\anclora_celery.bat"
echo echo Esperando 15 segundos a que Flask este listo... >> "%TEMP%\anclora_celery.bat"
echo timeout /t 15 /nobreak >> "%TEMP%\anclora_celery.bat"
echo echo. >> "%TEMP%\anclora_celery.bat"
echo echo Iniciando Celery Worker... >> "%TEMP%\anclora_celery.bat"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2 >> "%TEMP%\anclora_celery.bat"
echo pause >> "%TEMP%\anclora_celery.bat"
goto :eof

:create_powershell_scripts
if !USE_VENV!==1 (
    set VENV_PS=^& '!PROJECT_FOLDER!\venv-py311\Scripts\Activate.ps1'
) else (
    set VENV_PS=Write-Host '[Usando Python del sistema]' -ForegroundColor Yellow
)

REM Backend PowerShell
echo Write-Host '==================================' -ForegroundColor Green > "%TEMP%\anclora_backend.ps1"
echo Write-Host '  BACKEND FLASK - Puerto 5175' -ForegroundColor Green >> "%TEMP%\anclora_backend.ps1"
echo Write-Host '  Carpeta: !PROJECT_FOLDER!' -ForegroundColor Gray >> "%TEMP%\anclora_backend.ps1"
echo Write-Host '==================================' -ForegroundColor Green >> "%TEMP%\anclora_backend.ps1"
echo Write-Host '' >> "%TEMP%\anclora_backend.ps1"
echo Set-Location '!PROJECT_FOLDER!' >> "%TEMP%\anclora_backend.ps1"
echo !VENV_PS! >> "%TEMP%\anclora_backend.ps1"
echo Set-Location backend >> "%TEMP%\anclora_backend.ps1"
echo Write-Host 'Instalando dependencias...' -ForegroundColor Yellow >> "%TEMP%\anclora_backend.ps1"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.ps1"
echo Write-Host 'Iniciando Flask...' -ForegroundColor Yellow >> "%TEMP%\anclora_backend.ps1"
echo python main.py >> "%TEMP%\anclora_backend.ps1"

REM Frontend PowerShell
echo Write-Host '==================================' -ForegroundColor Blue > "%TEMP%\anclora_frontend.ps1"
echo Write-Host ' FRONTEND REACT - Puerto 5178' -ForegroundColor Blue >> "%TEMP%\anclora_frontend.ps1"
echo Write-Host ' Carpeta: !PROJECT_FOLDER!\frontend' -ForegroundColor Gray >> "%TEMP%\anclora_frontend.ps1"
echo Write-Host '==================================' -ForegroundColor Blue >> "%TEMP%\anclora_frontend.ps1"
echo Write-Host '' >> "%TEMP%\anclora_frontend.ps1"
echo Set-Location '!PROJECT_FOLDER!\frontend' >> "%TEMP%\anclora_frontend.ps1"
echo Write-Host 'Instalando dependencias...' -ForegroundColor Yellow >> "%TEMP%\anclora_frontend.ps1"
echo npm install >> "%TEMP%\anclora_frontend.ps1"
echo Write-Host 'Iniciando Vite...' -ForegroundColor Yellow >> "%TEMP%\anclora_frontend.ps1"
echo npm start >> "%TEMP%\anclora_frontend.ps1"

REM Celery PowerShell
echo Write-Host '==================================' -ForegroundColor Magenta > "%TEMP%\anclora_celery.ps1"
echo Write-Host ' CELERY WORKER - Conversiones' -ForegroundColor Magenta >> "%TEMP%\anclora_celery.ps1"
echo Write-Host ' Carpeta: !PROJECT_FOLDER!\backend' -ForegroundColor Gray >> "%TEMP%\anclora_celery.ps1"
echo Write-Host '==================================' -ForegroundColor Magenta >> "%TEMP%\anclora_celery.ps1"
echo Write-Host '' >> "%TEMP%\anclora_celery.ps1"
echo Set-Location '!PROJECT_FOLDER!' >> "%TEMP%\anclora_celery.ps1"
echo !VENV_PS! >> "%TEMP%\anclora_celery.ps1"
echo Set-Location backend >> "%TEMP%\anclora_celery.ps1"
echo Write-Host 'Esperando 15 segundos...' -ForegroundColor Yellow >> "%TEMP%\anclora_celery.ps1"
echo Start-Sleep -Seconds 15 >> "%TEMP%\anclora_celery.ps1"
echo Write-Host 'Iniciando Celery Worker...' -ForegroundColor Yellow >> "%TEMP%\anclora_celery.ps1"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2 >> "%TEMP%\anclora_celery.ps1"
goto :eof

:create_bash_scripts
if !USE_VENV!==1 (
    set VENV_BASH=source '!PROJECT_FOLDER!/venv-py311/Scripts/activate'
) else (
    set VENV_BASH=echo '[Usando Python del sistema]'
)

REM Backend Bash
echo #!/bin/bash > "%TEMP%\anclora_backend.sh"
echo echo '==================================' >> "%TEMP%\anclora_backend.sh"
echo echo '  BACKEND FLASK - Puerto 5175' >> "%TEMP%\anclora_backend.sh"
echo echo '  Carpeta: !PROJECT_FOLDER!' >> "%TEMP%\anclora_backend.sh"
echo echo '==================================' >> "%TEMP%\anclora_backend.sh"
echo echo '' >> "%TEMP%\anclora_backend.sh"
echo cd '!PROJECT_FOLDER!' >> "%TEMP%\anclora_backend.sh"
echo !VENV_BASH! >> "%TEMP%\anclora_backend.sh"
echo cd backend >> "%TEMP%\anclora_backend.sh"
echo echo 'Instalando dependencias...' >> "%TEMP%\anclora_backend.sh"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.sh"
echo echo 'Iniciando Flask...' >> "%TEMP%\anclora_backend.sh"
echo python main.py >> "%TEMP%\anclora_backend.sh"
echo read -p 'Presiona Enter para cerrar' >> "%TEMP%\anclora_backend.sh"

REM Frontend Bash
echo #!/bin/bash > "%TEMP%\anclora_frontend.sh"
echo echo '==================================' >> "%TEMP%\anclora_frontend.sh"
echo echo ' FRONTEND REACT - Puerto 5178' >> "%TEMP%\anclora_frontend.sh"
echo echo ' Carpeta: !PROJECT_FOLDER!/frontend' >> "%TEMP%\anclora_frontend.sh"
echo echo '==================================' >> "%TEMP%\anclora_frontend.sh"
echo echo '' >> "%TEMP%\anclora_frontend.sh"
echo cd '!PROJECT_FOLDER!/frontend' >> "%TEMP%\anclora_frontend.sh"
echo echo 'Instalando dependencias...' >> "%TEMP%\anclora_frontend.sh"
echo npm install >> "%TEMP%\anclora_frontend.sh"
echo echo 'Iniciando Vite...' >> "%TEMP%\anclora_frontend.sh"
echo npm start >> "%TEMP%\anclora_frontend.sh"
echo read -p 'Presiona Enter para cerrar' >> "%TEMP%\anclora_frontend.sh"

REM Celery Bash
echo #!/bin/bash > "%TEMP%\anclora_celery.sh"
echo echo '==================================' >> "%TEMP%\anclora_celery.sh"
echo echo ' CELERY WORKER - Conversiones' >> "%TEMP%\anclora_celery.sh"
echo echo ' Carpeta: !PROJECT_FOLDER!/backend' >> "%TEMP%\anclora_celery.sh"
echo echo '==================================' >> "%TEMP%\anclora_celery.sh"
echo echo '' >> "%TEMP%\anclora_celery.sh"
echo cd '!PROJECT_FOLDER!' >> "%TEMP%\anclora_celery.sh"
echo !VENV_BASH! >> "%TEMP%\anclora_celery.sh"
echo cd backend >> "%TEMP%\anclora_celery.sh"
echo echo 'Esperando 15 segundos...' >> "%TEMP%\anclora_celery.sh"
echo sleep 15 >> "%TEMP%\anclora_celery.sh"
echo echo 'Iniciando Celery Worker...' >> "%TEMP%\anclora_celery.sh"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2 >> "%TEMP%\anclora_celery.sh"
echo read -p 'Presiona Enter para cerrar' >> "%TEMP%\anclora_celery.sh"
goto :eof

:launch_cmd_terminals
echo.
echo Abriendo 3 terminales CMD...
start "Backend" cmd /c "%TEMP%\anclora_backend.bat"
timeout /t 2 /nobreak >nul
start "Frontend" cmd /c "%TEMP%\anclora_frontend.bat"
timeout /t 2 /nobreak >nul
start "Celery" cmd /c "%TEMP%\anclora_celery.bat"
goto :eof

:launch_powershell_terminals
REM Verificar Windows Terminal
where wt >nul 2>&1
if !errorlevel!==0 (
    echo.
    echo Abriendo 3 pestañas en Windows Terminal...
    start "" wt new-tab --title "Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_backend.ps1"
    timeout /t 1 /nobreak >nul
    start "" wt new-tab --title "Frontend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_frontend.ps1"
    timeout /t 1 /nobreak >nul
    start "" wt new-tab --title "Celery" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_celery.ps1"
) else (
    echo.
    echo Abriendo 3 ventanas PowerShell...
    start "Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_backend.ps1"
    timeout /t 2 /nobreak >nul
    start "Frontend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_frontend.ps1"
    timeout /t 2 /nobreak >nul
    start "Celery" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_celery.ps1"
)
goto :eof

:launch_bash_terminals
echo.
echo Abriendo 3 terminales Bash...
start "Backend" bash "%TEMP%\anclora_backend.sh"
timeout /t 2 /nobreak >nul
start "Frontend" bash "%TEMP%\anclora_frontend.sh"
timeout /t 2 /nobreak >nul
start "Celery" bash "%TEMP%\anclora_celery.sh"
goto :eof