#!/usr/bin/env python3
"""
Test script to check if the analyze endpoint returns the correct data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.converter import suggest_best_pipeline
import json

def test_analyze_endpoint():
    print("[TEST] Testing analyze endpoint data structure")

    # Use the test PDF
    pdf_path = "../docs/pdf/Emergent-Build-Guide.pdf"

    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return

    print(f"[INFO] Testing with: {pdf_path}")

    try:
        # Call the suggest_best_pipeline function directly (same as the endpoint)
        result = suggest_best_pipeline(pdf_path)

        print("[SUCCESS] Analysis successful!")
        print("[RESULT] Result structure:")
        print(json.dumps(result, indent=2))

        # Check expected keys
        expected_keys = ['recommended', 'pipelines', 'analysis']
        for key in expected_keys:
            if key in result:
                print(f"[OK] {key}: Found")
            else:
                print(f"[ERROR] {key}: Missing")

        # Check pipelines structure
        if 'pipelines' in result and isinstance(result['pipelines'], list):
            print(f"[OK] pipelines is a list with {len(result['pipelines'])} items")

            if len(result['pipelines']) > 0:
                first_pipeline = result['pipelines'][0]
                print("[DETAILS] First pipeline structure:")
                for key, value in first_pipeline.items():
                    print(f"   - {key}: {value}")
        else:
            print("[ERROR] pipelines is not a list or missing")

    except Exception as e:
        print(f"[ERROR] Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyze_endpoint()