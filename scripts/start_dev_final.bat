@echo off
setlocal EnableDelayedExpansion
title Anclora PDF2EPUB - INICIAR (Redis + Celery Fix)
color 0A

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - INICIAR DESARROLLO
echo =====================================================
echo.

REM Obtener carpeta padre del script
for %%i in ("%~dp0..") do set "REPO_ROOT=%%~fi"

echo Carpeta del repositorio detectada:
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

    echo Carpeta seleccionada: !PROJECT_FOLDER!
) else (
    echo Opcion invalida. Usando carpeta actual.
    set "PROJECT_FOLDER=!REPO_ROOT!"
)

echo.
echo =====================================================
echo VERIFICANDO ESTRUCTURA Y DEPENDENCIAS...
echo =====================================================

REM Verificar estructura
if not exist "!PROJECT_FOLDER!\backend" (
    echo ERROR: No se encontro carpeta 'backend'
    pause
    exit /b 1
)

if not exist "!PROJECT_FOLDER!\frontend" (
    echo ERROR: No se encontro carpeta 'frontend'
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
    echo AVISO: Sin entorno virtual (usara Python del sistema)
)

REM Verificar Docker
echo.
echo Verificando Docker...
docker version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Docker no esta corriendo
    echo Inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)
echo OK: Docker disponible

echo.
echo =====================================================
echo CONFIGURANDO REDIS...
echo =====================================================

REM Limpiar Redis anterior
echo [1/4] Limpiando Redis anterior...
docker stop redis-anclora >nul 2>&1
docker rm redis-anclora >nul 2>&1

REM Verificar que puerto 6379 este libre
echo [2/4] Verificando puerto 6379...
netstat -an | find "6379" >nul
if !errorlevel!==0 (
    echo AVISO: Puerto 6379 en uso. Intentando continuar...
)

REM Iniciar Redis
echo [3/4] Iniciando Redis en Docker...
docker run -d ^
    --name redis-anclora ^
    -p 6379:6379 ^
    --restart unless-stopped ^
    redis:7-alpine ^
    redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes

if !errorlevel! neq 0 (
    echo ERROR: No se pudo iniciar Redis
    echo.
    echo Posibles soluciones:
    echo - Cerrar otros programas que usen puerto 6379
    echo - Reiniciar Docker Desktop
    echo - Ejecutar como administrador
    pause
    exit /b 1
)

REM Esperar y verificar Redis multiples veces
echo [4/4] Verificando Redis (puede tardar 10 segundos)...
set "REDIS_OK=0"

for /L %%i in (1,1,10) do (
    timeout /t 1 /nobreak >nul
    docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping >nul 2>&1
    if !errorlevel!==0 (
        set "REDIS_OK=1"
        goto :redis_ready
    )
    echo    Intento %%i/10...
)

:redis_ready
if "!REDIS_OK!"=="0" (
    echo ERROR: Redis no responde despues de 10 intentos
    echo.
    echo Ver logs de Redis:
    echo docker logs redis-anclora
    pause
    exit /b 1
)

echo OK: Redis funcionando correctamente en puerto 6379

REM Verificar conexion desde el host
echo.
echo Verificando conexion Redis desde Windows...
docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ set test_key "test_value" >nul 2>&1
if !errorlevel!==0 (
    echo OK: Redis acepta conexiones y comandos
    docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ del test_key >nul 2>&1
) else (
    echo ERROR: Redis no acepta comandos
    pause
    exit /b 1
)

echo.
echo =====================================================
echo SELECCIONAR TIPO DE TERMINAL
echo =====================================================
echo.
echo Que tipo de terminal usar?
echo.
echo [1] CMD        - Command Prompt
echo [2] PowerShell - Windows PowerShell (recomendado)
echo [3] Git Bash   - Bash en Windows
echo.
set /p TERMINAL_CHOICE=Elige opcion (1-3):

if "!TERMINAL_CHOICE!"=="1" (
    set "TERMINAL_TYPE=cmd"
    echo Seleccionado: Command Prompt
) else if "!TERMINAL_CHOICE!"=="2" (
    set "TERMINAL_TYPE=powershell"
    echo Seleccionado: PowerShell
) else if "!TERMINAL_CHOICE!"=="3" (
    set "TERMINAL_TYPE=bash"
    where bash >nul 2>&1
    if !errorlevel! neq 0 (
        echo AVISO: Git Bash no encontrado, usando PowerShell
        set "TERMINAL_TYPE=powershell"
    ) else (
        echo Seleccionado: Git Bash
    )
) else (
    echo Opcion invalida, usando PowerShell
    set "TERMINAL_TYPE=powershell"
)

echo.
echo =====================================================
echo CREANDO SCRIPTS OPTIMIZADOS...
echo =====================================================

REM Preparar comandos venv
if "!USE_VENV!"=="1" (
    set "VENV_CMD=call "!PROJECT_FOLDER!\venv-py311\Scripts\activate.bat""
    set "VENV_PS=& '!PROJECT_FOLDER!\venv-py311\Scripts\Activate.ps1'"
    set "VENV_BASH=source '!PROJECT_FOLDER!/venv-py311/Scripts/activate'"
) else (
    set "VENV_CMD=echo [Sin venv]"
    set "VENV_PS=Write-Host '[Sin venv]' -ForegroundColor Yellow"
    set "VENV_BASH=echo '[Sin venv]'"
)

REM Backend script (siempre se crea)
if "!TERMINAL_TYPE!"=="cmd" (
    (
        echo @echo off
        echo title Backend Flask - Puerto 5175
        echo color 02
        echo echo ====================================
        echo echo    BACKEND FLASK - Puerto 5175
        echo echo ====================================
        echo echo.
        echo cd /d "!PROJECT_FOLDER!"
        echo !VENV_CMD!
        echo cd backend
        echo echo Instalando/actualizando dependencias...
        echo pip install -r requirements.txt --quiet
        echo if errorlevel 1 ^(
        echo     echo ERROR: Fallo instalacion de dependencias
        echo     pause
        echo     exit /b 1
        echo ^)
        echo echo.
        echo echo Iniciando Flask en puerto 5175...
        echo python main.py
        echo pause
    ) > "%TEMP%\anclora_backend.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    (
        echo Write-Host '====================================' -ForegroundColor Green
        echo Write-Host '   BACKEND FLASK - Puerto 5175' -ForegroundColor Green
        echo Write-Host '====================================' -ForegroundColor Green
        echo Write-Host ''
        echo Set-Location '!PROJECT_FOLDER!'
        echo !VENV_PS!
        echo Set-Location backend
        echo Write-Host 'Instalando/actualizando dependencias...' -ForegroundColor Yellow
        echo pip install -r requirements.txt --quiet
        echo if ^($LASTEXITCODE -ne 0^) {
        echo     Write-Host 'ERROR: Fallo instalacion de dependencias' -ForegroundColor Red
        echo     Read-Host 'Presiona Enter'
        echo     exit 1
        echo }
        echo Write-Host 'Iniciando Flask en puerto 5175...' -ForegroundColor Yellow
        echo python main.py
    ) > "%TEMP%\anclora_backend.ps1"
)

REM Frontend script
if "!TERMINAL_TYPE!"=="cmd" (
    (
        echo @echo off
        echo title Frontend React - Puerto 5178
        echo color 09
        echo echo ====================================
        echo echo   FRONTEND REACT - Puerto 5178
        echo echo ====================================
        echo echo.
        echo cd /d "!PROJECT_FOLDER!\frontend"
        echo echo Instalando/actualizando dependencias...
        echo npm install --silent
        echo if errorlevel 1 ^(
        echo     echo ERROR: Fallo npm install
        echo     pause
        echo     exit /b 1
        echo ^)
        echo echo.
        echo echo Iniciando Vite en puerto 5178...
        echo npm start
        echo pause
    ) > "%TEMP%\anclora_frontend.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    (
        echo Write-Host '====================================' -ForegroundColor Blue
        echo Write-Host '  FRONTEND REACT - Puerto 5178' -ForegroundColor Blue
        echo Write-Host '====================================' -ForegroundColor Blue
        echo Write-Host ''
        echo Set-Location '!PROJECT_FOLDER!\frontend'
        echo Write-Host 'Instalando/actualizando dependencias...' -ForegroundColor Yellow
        echo npm install --silent
        echo if ^($LASTEXITCODE -ne 0^) {
        echo     Write-Host 'ERROR: Fallo npm install' -ForegroundColor Red
        echo     Read-Host 'Presiona Enter'
        echo     exit 1
        echo }
        echo Write-Host 'Iniciando Vite en puerto 5178...' -ForegroundColor Yellow
        echo npm start
    ) > "%TEMP%\anclora_frontend.ps1"
)

REM Celery script CON verificacion Redis
if "!TERMINAL_TYPE!"=="cmd" (
    (
        echo @echo off
        echo title Celery Worker - Conversiones
        echo color 05
        echo echo ====================================
        echo echo   CELERY WORKER - Conversiones
        echo echo ====================================
        echo echo.
        echo echo Esperando 20 segundos a que Backend este listo...
        echo timeout /t 20 /nobreak
        echo echo.
        echo echo Verificando conexion Redis...
        echo docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping ^>nul 2^>^&1
        echo if errorlevel 1 ^(
        echo     echo ERROR: Redis no responde. Celery no puede iniciar.
        echo     echo Verifica que Redis este corriendo: docker ps ^| find "redis-anclora"
        echo     pause
        echo     exit /b 1
        echo ^)
        echo echo OK: Redis conectado
        echo echo.
        echo cd /d "!PROJECT_FOLDER!"
        echo !VENV_CMD!
        echo cd backend
        echo echo Verificando variables de entorno Redis...
        echo set ^| find "CELERY"
        echo echo.
        echo echo Iniciando Celery Worker...
        echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
        echo echo.
        echo echo Celery Worker detenido
        echo pause
    ) > "%TEMP%\anclora_celery.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    (
        echo Write-Host '====================================' -ForegroundColor Magenta
        echo Write-Host '  CELERY WORKER - Conversiones' -ForegroundColor Magenta
        echo Write-Host '====================================' -ForegroundColor Magenta
        echo Write-Host ''
        echo Write-Host 'Esperando 20 segundos a que Backend este listo...' -ForegroundColor Yellow
        echo Start-Sleep -Seconds 20
        echo Write-Host ''
        echo Write-Host 'Verificando conexion Redis...' -ForegroundColor Yellow
        echo $redisTest = docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping 2^>$null
        echo if ^($LASTEXITCODE -ne 0^) {
        echo     Write-Host 'ERROR: Redis no responde. Celery no puede iniciar.' -ForegroundColor Red
        echo     Write-Host 'Verifica: docker ps | findstr redis-anclora' -ForegroundColor Red
        echo     Read-Host 'Presiona Enter'
        echo     exit 1
        echo }
        echo Write-Host 'OK: Redis conectado' -ForegroundColor Green
        echo Write-Host ''
        echo Set-Location '!PROJECT_FOLDER!'
        echo !VENV_PS!
        echo Set-Location backend
        echo Write-Host 'Variables de entorno Redis:' -ForegroundColor Cyan
        echo Get-ChildItem Env: ^| Where-Object Name -like "*CELERY*"
        echo Write-Host 'Iniciando Celery Worker...' -ForegroundColor Yellow
        echo celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
    ) > "%TEMP%\anclora_celery.ps1"
)

echo.
echo =====================================================
echo ABRIENDO TERMINALES...
echo =====================================================

REM Abrir terminales en orden
echo [1/3] Abriendo Backend...
if "!TERMINAL_TYPE!"=="cmd" (
    start "Backend Flask" cmd /c "%TEMP%\anclora_backend.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    where wt >nul 2>&1
    if !errorlevel!==0 (
        start "" wt new-tab --title "Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_backend.ps1"
    ) else (
        start "Backend Flask" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_backend.ps1"
    )
)

timeout /t 3 /nobreak >nul

echo [2/3] Abriendo Frontend...
if "!TERMINAL_TYPE!"=="cmd" (
    start "Frontend React" cmd /c "%TEMP%\anclora_frontend.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    where wt >nul 2>&1
    if !errorlevel!==0 (
        start "" wt new-tab --title "Frontend" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_frontend.ps1"
    ) else (
        start "Frontend React" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_frontend.ps1"
    )
)

timeout /t 3 /nobreak >nul

echo [3/3] Abriendo Celery Worker...
if "!TERMINAL_TYPE!"=="cmd" (
    start "Celery Worker" cmd /c "%TEMP%\anclora_celery.bat"
) else if "!TERMINAL_TYPE!"=="powershell" (
    where wt >nul 2>&1
    if !errorlevel!==0 (
        start "" wt new-tab --title "Celery" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_celery.ps1"
    ) else (
        start "Celery Worker" powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP%\anclora_celery.ps1"
    )
)

echo.
echo =====================================================
echo DESARROLLO INICIADO CON REDIS Y CELERY
echo =====================================================
echo.
echo Configuracion:
echo   Carpeta: !PROJECT_FOLDER!
echo   Terminal: !TERMINAL_TYPE!
echo   Venv: !USE_VENV! (1=si, 0=no)
echo.
echo Servicios:
echo   Redis    - localhost:6379 (Docker: redis-anclora)
echo   Backend  - http://localhost:5175
echo   Frontend - http://localhost:5178  ^<-- ACCEDE AQUI
echo   Celery   - Worker para conversiones PDF
echo.
echo VERIFICAR REDIS:
echo   docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping
echo.
echo Para DETENER: stop_dev.bat
echo.

timeout /t 5 /nobreak >nul
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
exit /b 0