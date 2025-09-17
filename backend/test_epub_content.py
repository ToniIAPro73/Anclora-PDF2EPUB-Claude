#!/usr/bin/env python3
"""
Verificar el contenido del EPUB generado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ebooklib
from ebooklib import epub

def test_epub_content():
    print("[TEST] Verificando contenido del EPUB generado")

    epub_path = "test_output/test_conversion.epub"

    if not os.path.exists(epub_path):
        print(f"[ERROR] EPUB no encontrado: {epub_path}")
        return

    try:
        # Leer el EPUB
        book = epub.read_epub(epub_path)

        # Información básica
        print(f"[INFO] Título: {book.get_metadata('DC', 'title')}")
        print(f"[INFO] Idioma: {book.get_metadata('DC', 'language')}")
        print(f"[INFO] Creador: {book.get_metadata('DC', 'creator')}")

        # Obtener todos los elementos
        items = list(book.get_items())
        print(f"[INFO] Total de elementos: {len(items)}")

        # Contar tipos de elementos
        documents = []
        images = []
        other = []

        for item in items:
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                documents.append(item)
            elif item.get_type() == ebooklib.ITEM_IMAGE:
                images.append(item)
            else:
                other.append(item)

        print(f"[INFO] Documentos HTML: {len(documents)}")
        print(f"[INFO] Imágenes: {len(images)}")
        print(f"[INFO] Otros elementos: {len(other)}")

        # Mostrar contenido de las primeras páginas
        print("\n[CONTENIDO] Primeras páginas:")
        for i, doc in enumerate(documents[:3]):
            print(f"\n--- Página {i+1}: {doc.get_name()} ---")
            content = doc.get_content().decode('utf-8', errors='ignore')
            # Extraer texto visible (simplificado)
            import re
            text_content = re.sub(r'<[^>]+>', '', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()

            # Mostrar primeros 200 caracteres
            if text_content:
                preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                print(preview)
            else:
                print("[Sin texto visible]")

        print(f"\n[SUCCESS] EPUB válido con {len(documents)} páginas de contenido")

    except Exception as e:
        print(f"[ERROR] Error al leer EPUB: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_epub_content()