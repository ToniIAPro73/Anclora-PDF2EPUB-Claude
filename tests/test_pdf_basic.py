#!/usr/bin/env python3
"""
Test basico de validacion PDF sin emojis
"""

import os
from pathlib import Path

def test_pdf_basic(pdf_path):
    """Prueba basica de validacion PDF"""

    print(f"\n[PDF] Probando: {Path(pdf_path).name}")
    print("-" * 50)

    if not os.path.exists(pdf_path):
        print("[ERROR] Archivo no encontrado")
        return False

    # Informacion basica
    file_size = os.path.getsize(pdf_path)
    print(f"[SIZE] Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    # Test 1: Leer cabecera PDF
    try:
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            print(f"[HEADER] Cabecera: {header}")

            if header.startswith(b'%PDF-'):
                print("[OK] Cabecera PDF valida")
                version = header[5:8].decode('ascii', errors='ignore')
                print(f"[VERSION] Version PDF: {version}")
            else:
                print("[ERROR] Cabecera PDF invalida")
                return False

    except Exception as e:
        print(f"[ERROR] Error leyendo archivo: {e}")
        return False

    # Test 2: Verificar tamaño
    max_size = 25 * 1024 * 1024  # 25MB
    if file_size > max_size:
        print(f"[ERROR] Archivo demasiado grande (max {max_size/1024/1024}MB)")
        return False
    else:
        print("[OK] Tamaño dentro del limite")

    # Test 3: Buscar patrones maliciosos basicos
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read(10000)  # Solo primeros 10KB para rapidez

            dangerous_patterns = [b'/JavaScript', b'/JS', b'/OpenAction', b'/AA']
            found_patterns = []

            for pattern in dangerous_patterns:
                if pattern in content:
                    found_patterns.append(pattern.decode('ascii'))

            if found_patterns:
                print(f"[WARNING] Patrones sospechosos encontrados: {found_patterns}")
                return False
            else:
                print("[OK] No se detectaron patrones maliciosos")

    except Exception as e:
        print(f"[WARNING] Error escaneando contenido: {e}")

    # Test 4: Intentar leer con PyPDF2
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f, strict=False)

            if reader.is_encrypted:
                print("[ERROR] PDF esta encriptado")
                return False
            else:
                print("[OK] PDF no esta encriptado")

            try:
                page_count = len(reader.pages)
                print(f"[PAGES] Numero de paginas: {page_count}")
                if page_count == 0:
                    print("[ERROR] PDF sin paginas")
                    return False
                else:
                    print("[OK] PDF con paginas validas")
            except Exception as e:
                print(f"[WARNING] No se pudo determinar paginas: {e}")

    except ImportError:
        print("[WARNING] PyPDF2 no disponible, saltando test avanzado")
    except Exception as e:
        print(f"[WARNING] Error con PyPDF2: {e}")

    print("[SUCCESS] VALIDACION BASICA EXITOSA")
    return True


def main():
    """Funcion principal de pruebas"""

    print("Test Simple del Validador PDF")
    print("=" * 60)

    # Lista de PDFs a probar
    pdf_files = [
        "docs/pdf/Guia de identidad Visual de Anclora.pdf",
        "docs/pdf/BOE-A-2019-3814.pdf",
        "docs/pdf/Algoritmos graficos en Python_ BFS, DFS y mas.pdf",
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
            print(f"\n[SKIP] No encontrado: {pdf_file}")
            results[pdf_file] = None

    # Resumen
    print(f"\n[SUMMARY] RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for file_path, result in results.items():
        file_name = Path(file_path).name
        if result is True:
            print(f"[OK] {file_name}")
        elif result is False:
            print(f"[FAIL] {file_name}")
        else:
            print(f"[SKIP] {file_name} (no encontrado)")

    print(f"\n[RESULTS] Pasaron: {passed} | Fallaron: {failed} | Omitidos: {skipped}")

    if failed == 0 and passed > 0:
        print("[SUCCESS] Todos los PDFs disponibles pasaron la validacion!")
    elif failed > 0:
        print("[ERROR] Algunos PDFs fallaron. Verificar configuracion.")


if __name__ == "__main__":
    main()