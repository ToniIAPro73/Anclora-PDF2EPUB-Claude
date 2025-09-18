@echo off
setlocal enabledelayedexpansion

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - CONVERSION SIMPLE
echo =====================================================
echo.

REM Detectar carpeta del proyecto
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo Ubicacion: %PROJECT_DIR%

REM Verificar entorno virtual
if not exist "venv-py311\Scripts\python.exe" (
    echo ERROR: Entorno virtual no encontrado
    echo Ejecuta primero: python -m venv venv-py311
    pause
    exit /b 1
)

echo OK: Entorno virtual encontrado

REM Mostrar PDFs disponibles
echo.
echo PDFs disponibles en docs/pdf/:
echo.
set count=0
for %%f in ("docs\pdf\*.pdf") do (
    set /a count+=1
    echo !count!^) %%~nxf
    set "pdf!count!=%%f"
)

if %count%==0 (
    echo No se encontraron archivos PDF en docs/pdf/
    pause
    exit /b 1
)

echo.
set /p choice="Selecciona el numero del PDF a convertir (1-%count%): "

REM Validar entrada
if !choice! LSS 1 goto invalid_choice
if !choice! GTR %count% goto invalid_choice

REM Obtener archivo seleccionado
set "selected_pdf=!pdf%choice%!"
echo.
echo PDF seleccionado: !selected_pdf!

REM Obtener nombre sin extension para el EPUB
for %%f in ("!selected_pdf!") do set "pdf_name=%%~nf"

REM Crear directorio de salida
if not exist "converted_epubs" mkdir "converted_epubs"

set "output_epub=converted_epubs\!pdf_name!.epub"

echo EPUB se guardara como: !output_epub!
echo.

REM Crear script Python temporal
echo import sys > temp_convert.py
echo import os >> temp_convert.py
echo sys.path.append('backend') >> temp_convert.py
echo from app.converter import EnhancedPDFToEPUBConverter, ConversionEngine >> temp_convert.py
echo. >> temp_convert.py
echo print("[CONVERSION] Iniciando conversion...") >> temp_convert.py
echo converter = EnhancedPDFToEPUBConverter()^^ >> temp_convert.py
echo result = converter.convert( >> temp_convert.py
echo     pdf_path=r"!selected_pdf!", >> temp_convert.py
echo     output_path=r"!output_epub!", >> temp_convert.py
echo     engine=ConversionEngine.RAPID, >> temp_convert.py
echo     metadata={'title': '!pdf_name!', 'language': 'es', 'author': 'Anclora'} >> temp_convert.py
echo ) >> temp_convert.py
echo. >> temp_convert.py
echo if result['success']: >> temp_convert.py
echo     print(f"[SUCCESS] Conversion exitosa: {result['output_path']}") >> temp_convert.py
echo     print(f"[INFO] Texto preservado: {result['quality_metrics']['text_preserved']}%%") >> temp_convert.py
echo     print(f"[INFO] Motor usado: {result['engine_used']}") >> temp_convert.py
echo     if os.path.exists(result['output_path']): >> temp_convert.py
echo         size = os.path.getsize(result['output_path']) >> temp_convert.py
echo         print(f"[INFO] Tamaño del EPUB: {size} bytes ({size/1024:.1f} KB)") >> temp_convert.py
echo else: >> temp_convert.py
echo     print(f"[ERROR] Conversion fallida: {result['message']}") >> temp_convert.py

echo Ejecutando conversion...
echo.

REM Ejecutar conversion
venv-py311\Scripts\python.exe temp_convert.py

REM Limpiar archivo temporal
del temp_convert.py

echo.
echo =====================================================

REM Verificar si se creo el archivo
if exist "!output_epub!" (
    echo CONVERSION COMPLETADA EXITOSAMENTE
    echo.
    echo Archivo EPUB creado: !output_epub!
    echo.
    echo ¿Quieres abrir la carpeta de EPUBs convertidos?
    set /p open_folder="[S/N]: "
    if /i "!open_folder!"=="S" explorer "converted_epubs"
) else (
    echo ERROR: No se pudo crear el archivo EPUB
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
exit /b 0

:invalid_choice
echo.
echo ERROR: Seleccion invalida
echo.
goto end

:end
pause
exit /b 1