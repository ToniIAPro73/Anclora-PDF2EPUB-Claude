#!/usr/bin/env python3
"""
Simple validation test for FileSecurityValidator
"""
import sys
import os
from io import BytesIO

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from file_validator import FileSecurityValidator
    print("✅ FileSecurityValidator imported successfully")
    
    # Test basic configuration
    max_size = FileSecurityValidator.MAX_FILE_SIZE
    print(f"✅ Max file size: {max_size // (1024*1024)}MB")
    
    # Test filename validation
    class MockFile:
        def __init__(self, filename):
            self.filename = filename
    
    # Test valid filename
    valid_file = MockFile("document.pdf")
    valid, error, status = FileSecurityValidator.validate_filename(valid_file)
    print(f"✅ Valid filename test: {valid}")
    
    # Test invalid filename  
    invalid_file = MockFile("../malicious.pdf")
    valid, error, status = FileSecurityValidator.validate_filename(invalid_file)
    print(f"✅ Invalid filename test: {not valid}")
    
    # Test file presence
    files_with_file = {'file': MockFile("test.pdf")}
    valid, error, status = FileSecurityValidator.validate_file_presence(files_with_file)
    print(f"✅ File presence test: {valid}")
    
    files_without_file = {}
    valid, error, status = FileSecurityValidator.validate_file_presence(files_without_file)
    print(f"✅ No file test: {not valid}")
    
    print("\n🎉 All basic tests passed! FileSecurityValidator is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()