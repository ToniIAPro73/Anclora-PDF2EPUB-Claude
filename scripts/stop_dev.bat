@echo off
title Anclora PDF2EPUB - DETENER Desarrollo
color 0C

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - DETENER DESARROLLO
echo =====================================================
echo.

echo Deteniendo servicios de Anclora PDF2EPUB...
echo.

REM Detener Redis container
echo [1/4] Deteniendo Redis...
docker stop redis-anclora >nul 2>&1
if %errorlevel%==0 (
    echo      OK: Redis detenido
) else (
    echo      AVISO: Redis no estaba corriendo o ya fue detenido
)

echo [2/4] Eliminando contenedor Redis...
docker rm redis-anclora >nul 2>&1
if %errorlevel%==0 (
    echo      OK: Contenedor Redis eliminado
) else (
    echo      AVISO: Contenedor Redis no encontrado
)

REM Buscar y cerrar procesos relacionados con el proyecto
echo [3/4] Cerrando procesos Python (Flask/Celery)...

REM Cerrar procesos Python que puedan ser Flask o Celery
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    set "pid=%%i"
    set "pid=!pid:"=!"
    taskkill /pid !pid! /f >nul 2>&1
)

REM Cerrar procesos Node (React/Vite)
echo [4/4] Cerrando procesos Node (React/Vite)...
taskkill /f /im node.exe >nul 2>&1

REM Limpiar archivos temporales de los scripts
echo.
echo Limpiando archivos temporales...
del "%TEMP%\anclora_backend.bat" >nul 2>&1
del "%TEMP%\anclora_frontend.bat" >nul 2>&1
del "%TEMP%\anclora_celery.bat" >nul 2>&1
del "%TEMP%\backend.ps1" >nul 2>&1
del "%TEMP%\frontend.ps1" >nul 2>&1
del "%TEMP%\celery.ps1" >nul 2>&1
echo OK: Archivos temporales eliminados

REM Verificar puertos liberados
echo.
echo Verificando puertos...
netstat -an | find "5175" >nul
if %errorlevel%==0 (
    echo AVISO: Puerto 5175 (Backend) aun en uso
) else (
    echo OK: Puerto 5175 (Backend) liberado
)

netstat -an | find "5178" >nul
if %errorlevel%==0 (
    echo AVISO: Puerto 5178 (Frontend) aun en uso
) else (
    echo OK: Puerto 5178 (Frontend) liberado
)

netstat -an | find "6379" >nul
if %errorlevel%==0 (
    echo AVISO: Puerto 6379 (Redis) aun en uso
) else (
    echo OK: Puerto 6379 (Redis) liberado
)

echo.
echo =====================================================
echo DESARROLLO DETENIDO COMPLETAMENTE
echo =====================================================
echo.
echo Todos los servicios de Anclora PDF2EPUB han sido detenidos:
echo  [X] Backend Flask (Puerto 5175)
echo  [X] Frontend React (Puerto 5178)
echo  [X] Celery Worker (Conversiones)
echo  [X] Redis Database (Puerto 6379)
echo.
echo Las terminales pueden cerrarse manualmente si siguen abiertas.
echo.
echo Para volver a iniciar: ejecuta start_dev.bat
echo.

pause