#!/usr/bin/env python3
"""
Test script para probar el FileSecurityValidator con un PDF real
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.file_validator import FileSecurityValidator
from werkzeug.datastructures import FileStorage
import io

def test_pdf_validation(pdf_path):
    print(f"🧪 Testing PDF validation for: {pdf_path}")
    print(f"📁 File exists: {os.path.exists(pdf_path)}")

    if not os.path.exists(pdf_path):
        print("❌ File not found!")
        return

    # Read the PDF file
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()

    # Create a FileStorage object (simulates uploaded file)
    pdf_filename = os.path.basename(pdf_path)
    file_storage = FileStorage(
        stream=io.BytesIO(pdf_content),
        filename=pdf_filename,
        content_type='application/pdf'
    )

    # Create files dict as expected by the validator
    files = {'file': file_storage}

    print(f"📊 File size: {len(pdf_content)} bytes ({len(pdf_content)/1024/1024:.2f} MB)")
    print(f"📝 Filename: {pdf_filename}")

    # Test the validation
    print("\n🔍 Running FileSecurityValidator.validate_file_comprehensive...")
    try:
        valid, error_response, status_code, file_info = FileSecurityValidator.validate_file_comprehensive(files)

        print(f"\n✅ Validation result: {'PASSED' if valid else 'FAILED'}")

        if valid:
            print("🎉 PDF validation successful!")
            if file_info:
                print(f"📄 File info: {file_info}")
        else:
            print(f"❌ Validation failed with status {status_code}")
            print(f"🚫 Error: {error_response}")

    except Exception as e:
        print(f"💥 Exception during validation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with the specific PDF requested
    test_file = "docs/pdf/Emergent-Build-Guide.pdf"

    print("="*60)
    test_pdf_validation(test_file)
    print("="*60)
    print("🏁 Validation test completed!")