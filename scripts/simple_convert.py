#!/usr/bin/env python3
"""
Script simple para convertir Prompts Roboneo a EPUB en modo batch
"""

import sys
import os

# Añadir backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.converter import EnhancedPDFToEPUBConverter, ConversionEngine

def main():
    print("=" * 50)
    print("ANCLORA PDF2EPUB - CONVERSION SIMPLE")
    print("=" * 50)
    print()

    # Rutas
    pdf_path = "docs/pdf/Prompts Roboneo.pdf"
    output_dir = "converted_epubs"
    epub_path = os.path.join(output_dir, "Prompts_Roboneo.epub")

    # Verificar PDF
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF no encontrado: {pdf_path}")
        return

    print(f"PDF: {pdf_path}")

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    print(f"EPUB: {epub_path}")
    print()

    try:
        print("Iniciando conversión...")

        # Crear conversor
        converter = EnhancedPDFToEPUBConverter()

        # Convertir
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

        print()
        print("RESULTADO:")
        print(f"  - Éxito: {result['success']}")
        print(f"  - Mensaje: {result['message']}")
        print(f"  - Motor: {result['engine_used']}")
        print(f"  - Pipeline: {result['pipeline_used']}")
        print(f"  - Texto preservado: {result['quality_metrics']['text_preserved']}%")

        if result['success'] and os.path.exists(epub_path):
            size = os.path.getsize(epub_path)
            print(f"  - Archivo creado: {epub_path}")
            print(f"  - Tamaño: {size} bytes ({size/1024:.1f} KB)")
            print()
            print("=" * 50)
            print("✅ CONVERSIÓN EXITOSA")
            print("=" * 50)
        else:
            print()
            print("❌ Error: No se creó el archivo EPUB")

    except Exception as e:
        print(f"ERROR durante la conversión: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()