#!/bin/bash

# Script para ejecutar el entorno de producción
echo "🚀 Iniciando Anclora PDF2EPUB en modo producción..."
echo "📦 Esto construirá la aplicación y la servirá de forma optimizada"
echo ""

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down

# Construir y ejecutar
echo "🔨 Construyendo y ejecutando contenedores..."
docker-compose up --build

echo "✅ Aplicación disponible en http://localhost"
echo "🌐 Frontend: Puerto 5178"
echo "🔧 Backend: Puerto 5175"
echo "📊 Grafana: Puerto 3004"
