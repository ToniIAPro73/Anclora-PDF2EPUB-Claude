#!/usr/bin/env python3
"""
Test del endpoint de descarga
"""

import requests
import os

def test_download_endpoint():
    print("[TEST] Probando endpoint de descarga")

    # URL del backend (ajustar puerto si es necesario)
    base_url = "http://localhost:5175"
    filename = "prompts_roboneo.epub"

    # Verificar que el archivo existe
    epub_path = "test_output/prompts_roboneo.epub"
    if not os.path.exists(epub_path):
        print(f"[ERROR] Archivo EPUB no encontrado: {epub_path}")
        return

    file_size = os.path.getsize(epub_path)
    print(f"[INFO] Archivo EPUB encontrado: {file_size} bytes")

    # Probar descarga
    download_url = f"{base_url}/download/{filename}"
    print(f"[INFO] Probando descarga desde: {download_url}")

    try:
        response = requests.get(download_url, timeout=10)

        if response.status_code == 200:
            print(f"[SUCCESS] Descarga exitosa")
            print(f"[INFO] Content-Type: {response.headers.get('Content-Type')}")
            print(f"[INFO] Content-Length: {response.headers.get('Content-Length')}")
            print(f"[INFO] Content-Disposition: {response.headers.get('Content-Disposition')}")

            # Guardar archivo descargado para verificar
            download_path = "downloaded_prompts_roboneo.epub"
            with open(download_path, 'wb') as f:
                f.write(response.content)

            downloaded_size = os.path.getsize(download_path)
            print(f"[INFO] Archivo descargado: {downloaded_size} bytes")

            if downloaded_size == file_size:
                print("[SUCCESS] Tamaños coinciden - descarga correcta")
            else:
                print(f"[WARNING] Tamaños difieren: original={file_size}, descargado={downloaded_size}")

        else:
            print(f"[ERROR] Error en descarga: {response.status_code}")
            print(f"[ERROR] Respuesta: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se puede conectar al backend. ¿Está corriendo en {base_url}?")
    except Exception as e:
        print(f"[ERROR] Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_download_endpoint()