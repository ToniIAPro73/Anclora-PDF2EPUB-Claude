from app import create_app

app = create_app()

if __name__ == '__main__':
    try:
        print("Iniciando servidor Flask...")
        # Disable debug mode to avoid potential segfault issues
        app.run(host='0.0.0.0', port=5175, debug=False, threaded=True)
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para continuar...")