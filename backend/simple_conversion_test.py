#!/usr/bin/env python3
"""
Test simple de conversión PDF a EPUB usando solo la lógica básica
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.converter import EnhancedPDFToEPUBConverter, ConversionEngine
import tempfile

def simple_conversion_test():
    print("[TEST] Conversión simple PDF a EPUB")

    # PDF de prueba
    pdf_path = "../docs/pdf/Prompts Roboneo.pdf"

    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF no encontrado: {pdf_path}")
        return

    print(f"[INFO] Usando PDF: {pdf_path}")

    # Crear directorio de salida temporal
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    # Ruta de salida
    epub_path = os.path.join(output_dir, "prompts_roboneo.epub")

    print(f"[INFO] Archivo EPUB se guardará en: {epub_path}")

    try:
        # Crear conversor
        converter = EnhancedPDFToEPUBConverter()

        # Usar el motor más simple (RAPID)
        print("[INFO] Iniciando conversión con motor RAPID...")

        result = converter.convert(
            pdf_path=pdf_path,
            output_path=epub_path,
            engine=ConversionEngine.RAPID,
            metadata={
                'title': 'Prompts Roboneo',
                'language': 'es',
                'author': 'Anclora'
            }
        )

        print("[RESULTADO] Conversion result:")
        for key, value in result.items():
            if key != 'analysis':  # Skip large analysis object
                print(f"  - {key}: {value}")

        # Verificar si se creó el archivo
        if os.path.exists(epub_path):
            file_size = os.path.getsize(epub_path)
            print(f"[SUCCESS] Archivo EPUB creado: {epub_path}")
            print(f"[INFO] Tamaño del archivo: {file_size} bytes ({file_size/1024:.1f} KB)")

            # Verificar que es un ZIP válido (EPUB es un ZIP)
            import zipfile
            try:
                with zipfile.ZipFile(epub_path, 'r') as zf:
                    files = zf.namelist()
                    print(f"[INFO] Archivos dentro del EPUB: {len(files)}")
                    for file in files[:5]:  # Mostrar primeros 5 archivos
                        print(f"  - {file}")
                    if len(files) > 5:
                        print(f"  ... y {len(files) - 5} archivos más")

                print("[SUCCESS] El archivo EPUB es válido (estructura ZIP correcta)")
            except Exception as e:
                print(f"[ERROR] El archivo EPUB no es válido: {e}")
        else:
            print("[ERROR] No se creó el archivo EPUB")

    except Exception as e:
        print(f"[ERROR] Error durante la conversión: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_conversion_test()