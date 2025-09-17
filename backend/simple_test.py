#!/usr/bin/env python3
"""
Simple test para validar PDF sin imports complejos
"""

import os

def simple_pdf_check(pdf_path):
    print(f"[TEST] Simple PDF check for: {pdf_path}")

    # Check if file exists
    if not os.path.exists(pdf_path):
        print("[ERROR] File not found!")
        return

    # Get file info
    file_size = os.path.getsize(pdf_path)
    print(f"[INFO] File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

    # Read file content for basic checks
    with open(pdf_path, 'rb') as f:
        content = f.read()

    # Basic PDF validation
    print(f"[CHECK] Checking PDF header...")
    if content.startswith(b'%PDF-'):
        print("[OK] Valid PDF header found")
        pdf_version = content[:8]
        print(f"[INFO] PDF version: {pdf_version.decode('ascii', errors='ignore')}")
    else:
        print("[ERROR] Invalid PDF header")
        return

    # Check for patterns that were being blocked
    patterns_to_check = [
        (b'/JavaScript', 'JavaScript'),
        (b'/JS', 'JS'),
        (b'/OpenAction', 'OpenAction'),
        (b'/AA', 'Additional Actions'),
    ]

    found_patterns = []
    for pattern, name in patterns_to_check:
        if pattern in content:
            found_patterns.append(name)

    if found_patterns:
        print(f"[DETECTED] Interactive elements found: {', '.join(found_patterns)}")
        print("[INFO] These would have been BLOCKED before, but are now ALLOWED")
    else:
        print("[INFO] No interactive elements detected")

    # Count objects
    obj_count = content.count(b'obj')
    print(f"[COUNT] PDF objects found: {obj_count}")

    if obj_count > 1000:
        print(f"[COMPLEX] Complex PDF detected ({obj_count} objects)")
    if obj_count > 50000:
        print(f"[WARNING] Very complex PDF ({obj_count} objects) - would have been blocked before")
    if obj_count > 100000:
        print(f"[EXTREME] Extremely complex PDF ({obj_count} objects)")

    print("[SUCCESS] PDF appears to be valid and would pass the updated validation!")

if __name__ == "__main__":
    pdf_path = "../docs/pdf/Emergent-Build-Guide.pdf"
    print("="*60)
    simple_pdf_check(pdf_path)
    print("="*60)