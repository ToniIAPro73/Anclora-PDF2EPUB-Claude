#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "====================================================="
echo "ANCLORA PDF2EPUB - CONFIGURACION HIBRIDA + VENV"
echo "====================================================="
echo -e "${NC}"
echo "Este script configura desarrollo hibrido con entorno virtual:"
echo "• Redis en Docker (evita problemas Windows)"
echo "• Virtual Environment Python activado"
echo "• Backend Python local (hot reload)"
echo "• Frontend React local (hot reload)"
echo ""

# Verificar Docker
echo -e "${YELLOW}Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker no está instalado${NC}"
    exit 1
fi

if ! docker version &> /dev/null; then
    echo -e "${RED}ERROR: Docker no está corriendo. Por favor inicialo.${NC}"
    echo "    Abre Docker Desktop y espera a que esté listo."
    exit 1
fi
echo -e "${GREEN}OK: Docker listo${NC}"

# Verificar entorno virtual
echo -e "${YELLOW}Verificando entorno virtual...${NC}"
if [ ! -f "venv-py311/Scripts/activate" ] && [ ! -f "venv-py311/bin/activate" ]; then
    echo -e "${RED}ERROR: No se encuentra el entorno virtual venv-py311${NC}"
    echo "    Ejecuta: python -m venv venv-py311"
    exit 1
fi
echo -e "${GREEN}OK: Entorno virtual encontrado${NC}"

# Detener contenedores anteriores
echo -e "${YELLOW}Limpiando contenedores anteriores...${NC}"
docker stop redis-anclora &> /dev/null
docker rm redis-anclora &> /dev/null

# Iniciar Redis
echo -e "${YELLOW}Iniciando Redis en Docker...${NC}"
if ! docker run -d \
    --name redis-anclora \
    -p 6379:6379 \
    redis:7-alpine \
    redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes &> /dev/null; then
    echo -e "${RED}ERROR: Error iniciando Redis${NC}"
    exit 1
fi

echo -e "${GREEN}OK: Redis iniciado en puerto 6379${NC}"

# Esperar a que Redis esté listo
echo -e "${YELLOW}Esperando que Redis esté listo...${NC}"
sleep 3

# Verificar conexión Redis
echo -e "${YELLOW}Verificando conexión Redis...${NC}"
if ! docker exec redis-anclora redis-cli -a XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ ping &> /dev/null; then
    echo -e "${RED}ERROR: Redis no responde${NC}"
    exit 1
fi
echo -e "${GREEN}OK: Redis respondiendo correctamente${NC}"

echo ""
echo -e "${BLUE}"
echo "====================================================="
echo "CONFIGURACION HIBRIDA + VENV LISTA"
echo "====================================================="
echo -e "${NC}"
echo "Redis está corriendo en Docker en puerto 6379"
echo "Entorno virtual: venv-py311"
echo ""
echo -e "${YELLOW}PRÓXIMOS PASOS:${NC}"
echo ""
echo -e "${BLUE}=== GIT BASH / WSL / LINUX ===${NC}"
echo ""
echo "1. ACTIVAR ENTORNO VIRTUAL:"
echo "   source venv-py311/Scripts/activate"
echo "   # En Linux/Mac: source venv-py311/bin/activate"
echo ""
echo "2. BACKEND (Terminal con venv activado):"
echo "   cd backend"
echo "   pip install -r requirements.txt"
echo "   python main.py"
echo ""
echo "3. FRONTEND (Nueva terminal):"
echo "   cd frontend"
echo "   npm install"
echo "   npm start"
echo ""
echo "4. CELERY WORKER (Terminal con venv activado):"
echo "   cd backend"
echo "   celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet"
echo ""
echo -e "${YELLOW}URLs una vez iniciado todo:${NC}"
echo "   Frontend: http://localhost:5178"
echo "   Backend:  http://localhost:5175"
echo "   Redis:    localhost:6379"
echo ""
echo -e "${YELLOW}DESACTIVAR ENTORNO VIRTUAL:${NC}"
echo "   deactivate"
echo ""
echo -e "${YELLOW}Para detener Redis:${NC}"
echo "   docker stop redis-anclora"
echo ""