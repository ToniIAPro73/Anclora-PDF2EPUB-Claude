@echo off
echo 🚀 Iniciando Anclora PDF2EPUB en modo desarrollo...
echo 📝 Esto usará el Dockerfile de desarrollo que permite cambios dinámicos de idioma
echo.

echo 🛑 Deteniendo contenedores existentes...
docker-compose -f docker-compose.dev.yml down

echo 🔨 Construyendo y ejecutando contenedores...
docker-compose -f docker-compose.dev.yml up --build

echo ✅ Aplicación disponible en http://localhost
echo 🌐 Frontend: Puerto 5178
echo 🔧 Backend: Puerto 5175
echo 📊 Grafana: Puerto 3004
pause
