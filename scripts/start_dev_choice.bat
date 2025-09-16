@echo off
title Anclora PDF2EPUB - INICIAR con Selector de Terminal
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - INICIAR DESARROLLO
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
    echo ERROR: Docker no esta corriendo. Inicia Docker Desktop primero.
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
echo [1] CMD        - Command Prompt (Windows nativo)
echo [2] PowerShell - Windows PowerShell (recomendado)
echo [3] Git Bash   - Bash en Windows (requiere Git for Windows)
echo.
set /p TERMINAL_CHOICE=Elige una opcion (1-3):

if "%TERMINAL_CHOICE%"=="1" (
    set TERMINAL_TYPE=cmd
    echo Seleccionado: Command Prompt
) else if "%TERMINAL_CHOICE%"=="2" (
    set TERMINAL_TYPE=powershell
    echo Seleccionado: PowerShell
) else if "%TERMINAL_CHOICE%"=="3" (
    set TERMINAL_TYPE=bash
    echo Seleccionado: Git Bash
) else (
    echo Opcion invalida. Usando PowerShell por defecto.
    set TERMINAL_TYPE=powershell
)

echo.
echo =====================================================
echo CONFIGURANDO SERVICIOS...
echo =====================================================

REM Detener contenedores anteriores
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

REM Esperar Redis
echo Esperando que Redis este listo...
timeout /t 3 /nobreak >nul

docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Redis no responde
    pause
    exit /b 1
)
echo OK: Redis funcionando en puerto 6379

echo.
echo =====================================================
echo CREANDO SCRIPTS PARA %TERMINAL_TYPE%...
echo =====================================================

REM Preparar comandos segun terminal elegido
if "%TERMINAL_TYPE%"=="cmd" (
    call :create_cmd_scripts
) else if "%TERMINAL_TYPE%"=="powershell" (
    call :create_powershell_scripts
) else if "%TERMINAL_TYPE%"=="bash" (
    call :create_bash_scripts
)

REM Abrir terminales segun tipo elegido
echo.
echo Abriendo 3 terminales tipo %TERMINAL_TYPE%...
echo.

if "%TERMINAL_TYPE%"=="cmd" (
    call :launch_cmd_terminals
) else if "%TERMINAL_TYPE%"=="powershell" (
    call :launch_powershell_terminals
) else if "%TERMINAL_TYPE%"=="bash" (
    call :launch_bash_terminals
)

echo.
echo =====================================================
echo DESARROLLO INICIADO CON %TERMINAL_TYPE%
echo =====================================================
echo.
echo Ubicacion: %PROJECT_FOLDER%
echo Terminal:  %TERMINAL_TYPE%
echo.
echo Servicios:
echo  [Backend]  Flask en puerto 5175
echo  [Frontend] React en puerto 5178
echo  [Worker]   Celery conversiones
echo  [Redis]    Puerto 6379
echo.
echo ACCEDE A TU APLICACION:
echo  --^> http://localhost:5178
echo.

timeout /t 3 /nobreak >nul
pause
exit /b 0

REM ============ FUNCIONES PARA CREAR SCRIPTS ============

:create_cmd_scripts
if %USE_VENV%==1 (
    set VENV_CMD=call "%PROJECT_FOLDER%\venv-py311\Scripts\activate.bat"
) else (
    set VENV_CMD=echo [Sin entorno virtual]
)

REM Backend CMD
echo @echo off > "%TEMP%\anclora_backend.bat"
echo title [CMD] Backend Flask - Puerto 5175 >> "%TEMP%\anclora_backend.bat"
echo color 02 >> "%TEMP%\anclora_backend.bat"
echo echo ================================== >> "%TEMP%\anclora_backend.bat"
echo echo   BACKEND FLASK - Puerto 5175 >> "%TEMP%\anclora_backend.bat"
echo echo ================================== >> "%TEMP%\anclora_backend.bat"
echo cd /d "%PROJECT_FOLDER%" >> "%TEMP%\anclora_backend.bat"
echo %VENV_CMD% >> "%TEMP%\anclora_backend.bat"
echo cd backend >> "%TEMP%\anclora_backend.bat"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.bat"
echo python main.py >> "%TEMP%\anclora_backend.bat"
echo pause >> "%TEMP%\anclora_backend.bat"

REM Frontend CMD
echo @echo off > "%TEMP%\anclora_frontend.bat"
echo title [CMD] Frontend React - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo color 09 >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo echo  FRONTEND REACT - Puerto 5178 >> "%TEMP%\anclora_frontend.bat"
echo echo ================================== >> "%TEMP%\anclora_frontend.bat"
echo cd /d "%PROJECT_FOLDER%\frontend" >> "%TEMP%\anclora_frontend.bat"
echo npm install >> "%TEMP%\anclora_frontend.bat"
echo npm start >> "%TEMP%\anclora_frontend.bat"
echo pause >> "%TEMP%\anclora_frontend.bat"

REM Celery CMD
echo @echo off > "%TEMP%\anclora_celery.bat"
echo title [CMD] Celery Worker >> "%TEMP%\anclora_celery.bat"
echo color 05 >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo echo  CELERY WORKER - Conversiones >> "%TEMP%\anclora_celery.bat"
echo echo ================================== >> "%TEMP%\anclora_celery.bat"
echo cd /d "%PROJECT_FOLDER%" >> "%TEMP%\anclora_celery.bat"
echo %VENV_CMD% >> "%TEMP%\anclora_celery.bat"
echo cd backend >> "%TEMP%\anclora_celery.bat"
echo timeout /t 15 /nobreak >> "%TEMP%\anclora_celery.bat"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet >> "%TEMP%\anclora_celery.bat"
echo pause >> "%TEMP%\anclora_celery.bat"
goto :eof

:create_powershell_scripts
if %USE_VENV%==1 (
    set VENV_PS=^& '%PROJECT_FOLDER%\venv-py311\Scripts\Activate.ps1'
) else (
    set VENV_PS=Write-Host '[Sin entorno virtual]'
)

REM Backend PowerShell
echo Write-Host '==================================' -ForegroundColor Green > "%TEMP%\anclora_backend.ps1"
echo Write-Host '  BACKEND FLASK - Puerto 5175' -ForegroundColor Green >> "%TEMP%\anclora_backend.ps1"
echo Write-Host '==================================' -ForegroundColor Green >> "%TEMP%\anclora_backend.ps1"
echo Set-Location '%PROJECT_FOLDER%' >> "%TEMP%\anclora_backend.ps1"
echo %VENV_PS% >> "%TEMP%\anclora_backend.ps1"
echo Set-Location backend >> "%TEMP%\anclora_backend.ps1"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.ps1"
echo python main.py >> "%TEMP%\anclora_backend.ps1"

REM Frontend PowerShell
echo Write-Host '==================================' -ForegroundColor Blue > "%TEMP%\anclora_frontend.ps1"
echo Write-Host ' FRONTEND REACT - Puerto 5178' -ForegroundColor Blue >> "%TEMP%\anclora_frontend.ps1"
echo Write-Host '==================================' -ForegroundColor Blue >> "%TEMP%\anclora_frontend.ps1"
echo Set-Location '%PROJECT_FOLDER%\frontend' >> "%TEMP%\anclora_frontend.ps1"
echo npm install >> "%TEMP%\anclora_frontend.ps1"
echo npm start >> "%TEMP%\anclora_frontend.ps1"

REM Celery PowerShell
echo Write-Host '==================================' -ForegroundColor Magenta > "%TEMP%\anclora_celery.ps1"
echo Write-Host ' CELERY WORKER - Conversiones' -ForegroundColor Magenta >> "%TEMP%\anclora_celery.ps1"
echo Write-Host '==================================' -ForegroundColor Magenta >> "%TEMP%\anclora_celery.ps1"
echo Set-Location '%PROJECT_FOLDER%' >> "%TEMP%\anclora_celery.ps1"
echo %VENV_PS% >> "%TEMP%\anclora_celery.ps1"
echo Set-Location backend >> "%TEMP%\anclora_celery.ps1"
echo Start-Sleep -Seconds 15 >> "%TEMP%\anclora_celery.ps1"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet >> "%TEMP%\anclora_celery.ps1"
goto :eof

:create_bash_scripts
if %USE_VENV%==1 (
    set VENV_BASH=source '%PROJECT_FOLDER%/venv-py311/Scripts/activate'
) else (
    set VENV_BASH=echo '[Sin entorno virtual]'
)

REM Backend Bash
echo #!/bin/bash > "%TEMP%\anclora_backend.sh"
echo echo '==================================' >> "%TEMP%\anclora_backend.sh"
echo echo '  BACKEND FLASK - Puerto 5175' >> "%TEMP%\anclora_backend.sh"
echo echo '==================================' >> "%TEMP%\anclora_backend.sh"
echo cd '%PROJECT_FOLDER%' >> "%TEMP%\anclora_backend.sh"
echo %VENV_BASH% >> "%TEMP%\anclora_backend.sh"
echo cd backend >> "%TEMP%\anclora_backend.sh"
echo pip install -r requirements.txt >> "%TEMP%\anclora_backend.sh"
echo python main.py >> "%TEMP%\anclora_backend.sh"
echo read -p 'Presiona Enter para cerrar' >> "%TEMP%\anclora_backend.sh"

REM Frontend Bash
echo #!/bin/bash > "%TEMP%\anclora_frontend.sh"
echo echo '==================================' >> "%TEMP%\anclora_frontend.sh"
echo echo ' FRONTEND REACT - Puerto 5178' >> "%TEMP%\anclora_frontend.sh"
echo echo '==================================' >> "%TEMP%\anclora_frontend.sh"
echo cd '%PROJECT_FOLDER%/frontend' >> "%TEMP%\anclora_frontend.sh"
echo npm install >> "%TEMP%\anclora_frontend.sh"
echo npm start >> "%TEMP%\anclora_frontend.sh"
echo read -p 'Presiona Enter para cerrar' >> "%TEMP%\anclora_frontend.sh"

REM Celery Bash
echo #!/bin/bash > "%TEMP%\anclora_celery.sh"
echo echo '==================================' >> "%TEMP%\anclora_celery.sh"
echo echo ' CELERY WORKER - Conversiones' >> "%TEMP%\anclora_celery.sh"
echo echo '==================================' >> "%TEMP%\anclora_celery.sh"
echo cd '%PROJECT_FOLDER%' >> "%TEMP%\anclora_celery.sh"
echo %VENV_BASH% >> "%TEMP%\anclora_celery.sh"
echo cd backend >> "%TEMP%\anclora_celery.sh"
echo sleep 15 >> "%TEMP%\anclora_celery.sh"
echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet >> "%TEMP%\anclora_celery.sh"
echo read -p 'Presiona Enter para cerrar' >> "%TEMP%\anclora_celery.sh"
goto :eof

REM ============ FUNCIONES PARA LANZAR TERMINALES ============

:launch_cmd_terminals
start "[CMD] Backend" cmd /c "%TEMP%\anclora_backend.bat"
timeout /t 2 /nobreak >nul
start "[CMD] Frontend" cmd /c "%TEMP%\anclora_frontend.bat"
timeout /t 2 /nobreak >nul
start "[CMD] Celery" cmd /c "%TEMP%\anclora_celery.bat"
goto :eof

:launch_powershell_terminals
REM Verificar si Windows Terminal esta disponible
where wt >nul 2>&1
if %errorlevel%==0 (
    start "" wt new-tab --title "Backend" powershell -NoExit -File "%TEMP%\anclora_backend.ps1"
    timeout /t 2 /nobreak >nul
    start "" wt new-tab --title "Frontend" powershell -NoExit -File "%TEMP%\anclora_frontend.ps1"
    timeout /t 2 /nobreak >nul
    start "" wt new-tab --title "Celery" powershell -NoExit -File "%TEMP%\anclora_celery.ps1"
) else (
    start "[PS] Backend" powershell -NoExit -File "%TEMP%\anclora_backend.ps1"
    timeout /t 2 /nobreak >nul
    start "[PS] Frontend" powershell -NoExit -File "%TEMP%\anclora_frontend.ps1"
    timeout /t 2 /nobreak >nul
    start "[PS] Celery" powershell -NoExit -File "%TEMP%\anclora_celery.ps1"
)
goto :eof

:launch_bash_terminals
REM Verificar si Git Bash esta disponible
where bash >nul 2>&1
if %errorlevel%==0 (
    start "[Bash] Backend" bash "%TEMP%\anclora_backend.sh"
    timeout /t 2 /nobreak >nul
    start "[Bash] Frontend" bash "%TEMP%\anclora_frontend.sh"
    timeout /t 2 /nobreak >nul
    start "[Bash] Celery" bash "%TEMP%\anclora_celery.sh"
) else (
    echo ERROR: Git Bash no encontrado. Instala Git for Windows.
    echo Usando PowerShell como alternativa...
    call :create_powershell_scripts
    call :launch_powershell_terminals
)
goto :eof