#!/usr/bin/env python3
"""
Test simple y directo del validador PDF
"""

import os
from pathlib import Path

def test_pdf_basic(pdf_path):
    """Prueba básica de validación PDF"""

    print(f"\n[PDF] Probando: {Path(pdf_path).name}")
    print("-" * 40)

    if not os.path.exists(pdf_path):
        print("❌ Archivo no encontrado")
        return False

    # Información básica
    file_size = os.path.getsize(pdf_path)
    print(f"[SIZE] Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    # Test 1: Leer cabecera PDF
    try:
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            print(f"[HEADER] Cabecera: {header}")

            if header.startswith(b'%PDF-'):
                print("[OK] Cabecera PDF válida")
                version = header[5:8].decode('ascii', errors='ignore')
                print(f"[VERSION] Versión PDF: {version}")
            else:
                print("[ERROR] Cabecera PDF inválida")
                return False

    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

    # Test 2: Verificar tamaño
    max_size = 25 * 1024 * 1024  # 25MB
    if file_size > max_size:
        print(f"❌ Archivo demasiado grande (máx {max_size/1024/1024}MB)")
        return False
    else:
        print("✅ Tamaño dentro del límite")

    # Test 3: Buscar patrones maliciosos básicos
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read(10000)  # Solo primeros 10KB para rapidez

            dangerous_patterns = [b'/JavaScript', b'/JS', b'/OpenAction', b'/AA']
            found_patterns = []

            for pattern in dangerous_patterns:
                if pattern in content:
                    found_patterns.append(pattern.decode('ascii'))

            if found_patterns:
                print(f"⚠️  Patrones sospechosos encontrados: {found_patterns}")
                return False
            else:
                print("✅ No se detectaron patrones maliciosos")

    except Exception as e:
        print(f"⚠️  Error escaneando contenido: {e}")

    # Test 4: Intentar leer con PyPDF2
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f, strict=False)

            if reader.is_encrypted:
                print("❌ PDF está encriptado")
                return False
            else:
                print("✅ PDF no está encriptado")

            try:
                page_count = len(reader.pages)
                print(f"📑 Número de páginas: {page_count}")
                if page_count == 0:
                    print("❌ PDF sin páginas")
                    return False
                else:
                    print("✅ PDF con páginas válidas")
            except Exception as e:
                print(f"⚠️  No se pudo determinar páginas: {e}")

    except ImportError:
        print("⚠️  PyPDF2 no disponible, saltando test avanzado")
    except Exception as e:
        print(f"⚠️  Error con PyPDF2: {e}")

    print("✅ VALIDACIÓN BÁSICA EXITOSA")
    return True


def main():
    """Función principal de pruebas"""

    print("🚀 Test Simple del Validador PDF")
    print("=" * 50)

    # Lista de PDFs a probar
    pdf_files = [
        "docs/pdf/Guía de identidad Visual de Anclora.pdf",
        "docs/pdf/BOE-A-2019-3814.pdf",
        "docs/pdf/Algoritmos gráficos en Python_ BFS, DFS y más.pdf",
        "tests/sample.pdf",
        "backend/uploads/test.pdf"
    ]

    base_path = Path(__file__).parent
    results = {}

    for pdf_file in pdf_files:
        full_path = base_path / pdf_file
        if full_path.exists():
            results[pdf_file] = test_pdf_basic(str(full_path))
        else:
            print(f"\n⚠️  No encontrado: {pdf_file}")
            results[pdf_file] = None

    # Resumen
    print(f"\n📊 RESUMEN DE PRUEBAS")
    print("=" * 50)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for file_path, result in results.items():
        file_name = Path(file_path).name
        if result is True:
            print(f"✅ {file_name}")
        elif result is False:
            print(f"❌ {file_name}")
        else:
            print(f"⚠️  {file_name} (no encontrado)")

    print(f"\n🎯 Resultados: ✅ {passed} | ❌ {failed} | ⚠️ {skipped}")

    if failed == 0 and passed > 0:
        print("🎉 ¡Todos los PDFs disponibles pasaron la validación!")
    elif failed > 0:
        print("🚨 Algunos PDFs fallaron. Verificar configuración.")


if __name__ == "__main__":
    main()