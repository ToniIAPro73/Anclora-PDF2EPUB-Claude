# Desarrollo Hibrido - Redis Docker + Python/React Local

Este enfoque combina lo mejor de ambos mundos: **Redis en Docker** (sin problemas de Windows) y **desarrollo local** (hot reload rapido).

## Ventajas del Modelo Hibrido

- Sin problemas Redis/Windows: Redis corre en Docker
- Hot reload rapido: Backend y frontend en local
- Facil debugging: Acceso directo al codigo
- CORS resuelto: Configuracion automatica
- Celery funcional: Con eventlet para Windows

## Inicio Rapido

### 1. Ejecutar Script Automatico
```bash
# En Windows
scripts\setup_hybrid_dev_clean.bat

# El script automaticamente:
# - Inicia Redis en Docker
# - Configura variables de entorno
# - Te da los proximos pasos
```

### 2. Inicio Manual (Alternativa)

```bash
# 1. Iniciar Redis en Docker
docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes

# 2. Backend (Terminal 1)
cd backend
pip install -r requirements.txt
python main.py

# 3. Frontend (Terminal 2)
cd frontend
npm install
npm start

# 4. Celery Worker (Terminal 3 - Opcional)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet --concurrency=2
```

## URLs de Desarrollo

| Servicio | URL | Descripcion |
|----------|-----|-------------|
| Frontend | `http://localhost:5178` | Interfaz React |
| Backend | `http://localhost:5175` | API Flask |
| Redis | `localhost:6379` | Base de datos Redis |

## Configuracion

### Variables de Entorno (ya configuradas)
- backend/.env - Variables backend
- frontend/.env - Variables frontend
- CORS configurado para desarrollo local

### Puertos Utilizados
- **5178**: Frontend React (Vite)
- **5175**: Backend Flask
- **6379**: Redis Docker

## Solucion de Problemas

### Redis no conecta
```bash
# Verificar Redis
docker ps | grep redis-anclora

# Ver logs Redis
docker logs redis-anclora

# Reiniciar Redis
docker restart redis-anclora
```

### Celery falla en Windows
```bash
# Instalar eventlet (ya en requirements.txt)
pip install eventlet

# Usar pool eventlet
celery -A app.tasks.celery_app worker --pool=eventlet
```

### CORS Issues
- Ya configurado en `backend/app/__init__.py`
- Proxy configurado en `frontend/vite.config.js`

### Hot Reload no funciona
```bash
# Backend: usar modo debug
FLASK_ENV=development python main.py

# Frontend: verificar Vite
npm start
```

## Detener Desarrollo

```bash
# Detener Redis
docker stop redis-anclora

# Ctrl+C en cada terminal para backend/frontend
```

## Notas de Desarrollo

1. **Cambios en Backend**: Se reflejan automaticamente (Flask debug mode)
2. **Cambios en Frontend**: Hot reload inmediato (Vite)
3. **Cambios en Tasks**: Reiniciar Celery worker
4. **Redis persiste**: Los datos se mantienen entre reinicios

## Proximos Pasos

Una vez que funcione todo:
1. Verificar iconos en frontend
2. Probar conversion PDF -> EPUB
3. Verificar autenticacion Supabase
4. Testing completo

---

**Problemas?** Revisa los logs de cada servicio o ejecuta `scripts\setup_hybrid_dev_clean.bat` de nuevo.