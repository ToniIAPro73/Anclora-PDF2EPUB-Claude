@echo off
setlocal enabledelayedexpansion

echo.
echo =====================================================
echo ANCLORA PDF2EPUB - CONVERSION AUTOMATICA
echo =====================================================
echo.

REM Detectar carpeta del proyecto
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo Ubicacion: %PROJECT_DIR%

REM Verificar entorno virtual
if not exist "venv-py311\Scripts\python.exe" (
    echo ERROR: Entorno virtual no encontrado
    pause
    exit /b 1
)

echo OK: Entorno virtual encontrado

REM Archivo fijo para la prueba
set "selected_pdf=docs\pdf\Prompts Roboneo.pdf"

if not exist "!selected_pdf!" (
    echo ERROR: No se encuentra el archivo: !selected_pdf!
    pause
    exit /b 1
)

echo PDF seleccionado: !selected_pdf!

REM Crear directorio de salida
if not exist "converted_epubs" mkdir "converted_epubs"

set "output_epub=converted_epubs\Prompts_Roboneo.epub"

echo EPUB se guardara como: !output_epub!
echo.

REM Crear script Python temporal
echo import sys > temp_convert_auto.py
echo import os >> temp_convert_auto.py
echo sys.path.append('backend') >> temp_convert_auto.py
echo from app.converter import EnhancedPDFToEPUBConverter, ConversionEngine >> temp_convert_auto.py
echo. >> temp_convert_auto.py
echo print("[CONVERSION] Iniciando conversion de Prompts Roboneo...") >> temp_convert_auto.py
echo converter = EnhancedPDFToEPUBConverter() >> temp_convert_auto.py
echo result = converter.convert( >> temp_convert_auto.py
echo     pdf_path=r"!selected_pdf!", >> temp_convert_auto.py
echo     output_path=r"!output_epub!", >> temp_convert_auto.py
echo     engine=ConversionEngine.RAPID, >> temp_convert_auto.py
echo     metadata={'title': 'Prompts Roboneo', 'language': 'es', 'author': 'Anclora'} >> temp_convert_auto.py
echo ) >> temp_convert_auto.py
echo. >> temp_convert_auto.py
echo if result['success']: >> temp_convert_auto.py
echo     print(f"[SUCCESS] Conversion exitosa: {result['output_path']}") >> temp_convert_auto.py
echo     print(f"[INFO] Texto preservado: {result['quality_metrics']['text_preserved']}%%") >> temp_convert_auto.py
echo     print(f"[INFO] Motor usado: {result['engine_used']}") >> temp_convert_auto.py
echo     if os.path.exists(result['output_path']): >> temp_convert_auto.py
echo         size = os.path.getsize(result['output_path']) >> temp_convert_auto.py
echo         print(f"[INFO] Tamaño del EPUB: {size} bytes ({size/1024:.1f} KB)") >> temp_convert_auto.py
echo     print(f"[INFO] Pipeline usado: {result['pipeline_used']}") >> temp_convert_auto.py
echo else: >> temp_convert_auto.py
echo     print(f"[ERROR] Conversion fallida: {result['message']}") >> temp_convert_auto.py

echo Ejecutando conversion...
echo.

REM Ejecutar conversion
venv-py311\Scripts\python.exe temp_convert_auto.py

REM Verificar resultado
if exist "!output_epub!" (
    echo.
    echo =====================================================
    echo CONVERSION COMPLETADA EXITOSAMENTE
    echo =====================================================
    echo.
    echo Archivo EPUB creado: !output_epub!

    REM Mostrar información del archivo
    for %%I in ("!output_epub!") do (
        echo Tamaño: %%~zI bytes
        echo Fecha: %%~tI
    )

    echo.
    echo El archivo está listo para usar!
) else (
    echo.
    echo ERROR: No se pudo crear el archivo EPUB
)

REM Limpiar archivo temporal
del temp_convert_auto.py

echo.
pause