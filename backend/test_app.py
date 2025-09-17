#!/usr/bin/env python3
print("Testing app creation...")

try:
    from app import create_app
    print("OK: App import")

    app = create_app()
    print("OK: App created")

    print("Starting app in test mode...")
    # Don't run with debug=True as it might cause issues
    app.run(host='127.0.0.1', port=5175, debug=False)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()