#!/usr/bin/env python3
"""
Script de pruebas unitarias para el FileSecurityValidator
Permite probar la validación sin ejecutar la aplicación completa
"""

import sys
import os
from pathlib import Path
import re

# Variables de configuración básicas
os.environ['MAX_FILE_SIZE_MB'] = '25'

print("🔍 Probando validador de archivos PDF...")
print("=" * 50)


class MockFile:
    """Clase mock que simula werkzeug.FileStorage para testing"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name
        self.content = None
        self.position = 0

        # Leer contenido del archivo
        if self.file_path.exists():
            with open(self.file_path, 'rb') as f:
                self.content = f.read()
        else:
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    def read(self, size=-1):
        """Simula file.read()"""
        if size == -1:
            result = self.content[self.position:]
            self.position = len(self.content)
        else:
            result = self.content[self.position:self.position + size]
            self.position = min(self.position + size, len(self.content))
        return result

    def seek(self, pos, whence=0):
        """Simula file.seek()"""
        if whence == 0:  # SEEK_SET
            self.position = pos
        elif whence == 1:  # SEEK_CUR
            self.position += pos
        elif whence == 2:  # SEEK_END
            self.position = len(self.content) + pos
        self.position = max(0, min(self.position, len(self.content)))

    def tell(self):
        """Simula file.tell()"""
        return self.position


def test_pdf_file(pdf_path: str):
    """Prueba un archivo PDF específico con el validador"""

    print(f"\n🔍 Probando archivo: {pdf_path}")
    print("=" * 60)

    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return False

    try:
        # Crear mock file
        mock_file = MockFile(pdf_path)

        # Información básica del archivo
        file_size = len(mock_file.content)
        print(f"📄 Nombre: {mock_file.filename}")
        print(f"📏 Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

        # Simular request.files
        files = {'file': mock_file}

        # Ejecutar validación completa
        print(f"\n🧪 Ejecutando validación completa...")

        valid, error_response, status_code, file_info = FileSecurityValidator.validate_file_comprehensive(files)

        if valid:
            print("✅ VALIDACIÓN EXITOSA")
            if file_info:
                print(f"📋 Información del archivo:")
                for key, value in file_info.items():
                    if key == 'validations':
                        print(f"  {key}:")
                        for val_name, val_result in value.items():
                            status_icon = "✅" if val_result == "passed" else "❌" if val_result == "failed" else "⚠️"
                            print(f"    {status_icon} {val_name}: {val_result}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("❌ VALIDACIÓN FALLIDA")
            print(f"📛 Error: {error_response.get('error', 'Error desconocido')}")
            print(f"🔢 Código de estado: {status_code}")
            if error_response.get('details'):
                print(f"🔍 Detalles: {error_response['details']}")

            if file_info and 'validations' in file_info:
                print(f"\n📊 Resultados de validaciones individuales:")
                for val_name, val_result in file_info['validations'].items():
                    status_icon = "✅" if val_result == "passed" else "❌" if val_result == "failed" else "⚠️"
                    print(f"  {status_icon} {val_name}: {val_result}")

        return valid

    except Exception as e:
        print(f"💥 Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_validator_tests():
    """Ejecuta las pruebas del validador con archivos disponibles"""

    print("🚀 Iniciando pruebas del FileSecurityValidator")
    print("=" * 60)

    # Lista de archivos PDF para probar
    test_files = [
        "tests/sample.pdf",
        "backend/uploads/test.pdf",
    ]

    results = {}

    for pdf_path in test_files:
        full_path = Path(__file__).parent / pdf_path
        if full_path.exists():
            results[pdf_path] = test_pdf_file(str(full_path))
        else:
            print(f"\n⚠️  Archivo no encontrado: {pdf_path}")
            results[pdf_path] = None

    # Resumen de resultados
    print(f"\n📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for file_path, result in results.items():
        if result is True:
            print(f"✅ {file_path}: PASÓ")
        elif result is False:
            print(f"❌ {file_path}: FALLÓ")
        else:
            print(f"⚠️  {file_path}: OMITIDO (archivo no encontrado)")

    print(f"\n🎯 Resultados finales:")
    print(f"   ✅ Pasaron: {passed}")
    print(f"   ❌ Fallaron: {failed}")
    print(f"   ⚠️  Omitidos: {skipped}")

    if failed == 0 and passed > 0:
        print(f"\n🎉 ¡Todas las pruebas disponibles pasaron!")
        return True
    elif failed > 0:
        print(f"\n🚨 {failed} prueba(s) fallaron. Revisar configuración del validador.")
        return False
    else:
        print(f"\n⚠️  No se encontraron archivos PDF para probar.")
        return False


if __name__ == "__main__":
    success = run_validator_tests()
    sys.exit(0 if success else 1)