from app import create_app

app = create_app()

if __name__ == '__main__':
    try:
        print("Iniciando servidor Flask...")
        # Use port 5175 for local development
        app.run(host='127.0.0.1', port=5175, debug=True)
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para continuar...")