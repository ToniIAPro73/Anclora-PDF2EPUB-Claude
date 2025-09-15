@echo off
echo 🚀 Iniciando Anclora PDF2EPUB en modo producción...
echo 📦 Esto construirá la aplicación y la servirá de forma optimizada
echo.

echo 🛑 Deteniendo contenedores existentes...
docker-compose down

echo 🔨 Construyendo y ejecutando contenedores...
docker-compose up --build

echo ✅ Aplicación disponible en http://localhost
echo 🌐 Frontend: Puerto 5178
echo 🔧 Backend: Puerto 5175
echo 📊 Grafana: Puerto 3004
pause
