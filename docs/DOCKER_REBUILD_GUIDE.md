# 🐳 Guía de Rebuild Docker - Post Sprint 1.4

## Problemas Resueltos

✅ **Variables de entorno faltantes** - Agregadas a docker-compose.yml  
✅ **Node.js 18 → 20** - Actualizado para compatibilidad con Vite 7  
✅ **Problema Rollup** - Uso de `npm ci` para instalación limpia  
✅ **Supabase Keys** - New API keys agregadas a .env principal  

## 🔧 Comandos para Rebuild

### 1. Detener contenedores actuales
```bash
docker-compose down
```

### 2. Eliminar imágenes antiguas (forzar rebuild)
```bash
docker-compose down --rmi all --volumes --remove-orphans
```

### 3. Rebuild desde cero
```bash
docker-compose build --no-cache
```

### 4. Levantar servicios
```bash
docker-compose up -d
```

### 5. Verificar logs
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f frontend
docker-compose logs -f backend  
docker-compose logs -f worker
```

## 🔍 Verificación de Correcciones

### Frontend
✅ **Node.js 20** - Resuelve error "Vite requires Node.js version 20.19+"  
✅ **Rollup fix** - `npm ci` soluciona "@rollup/rollup-linux-x64-gnu"  
✅ **Build exitoso** - Debería compilar sin errores  

### Backend
✅ **Variables env** - FLASK_APP, FLASK_ENV, SECRET_KEY disponibles  
✅ **Redis password** - REDIS_PASSWORD configurado  
✅ **Supabase keys** - New API keys (sb_publishable_, sb_secret_)  

### Worker
✅ **Celery config** - Todas las variables requeridas  
✅ **Supabase access** - Mismas keys que backend  
✅ **Redis connection** - Conexión a Redis con password  

## ⚠️ Si persisten errores

### Error "Invalid API key" en Supabase
```bash
# Verificar que las keys estén disponibles en el contenedor
docker-compose exec backend env | grep SUPABASE
```

### Error de autenticación (401)
```bash
# Verificar configuración de auth en backend
docker-compose exec backend python -c "from app.config import ConfigManager; ConfigManager.initialize(); print('Config OK')"
```

### Error de Node.js/Rollup
```bash
# Verificar versión de Node en contenedor
docker-compose exec frontend node --version  # Debería ser v20.x
```

## 🚀 Testing Post-Rebuild

### 1. Verificar que todos los servicios estén up
```bash
docker-compose ps
```

### 2. Test de endpoints
```bash
# Health check backend
curl http://localhost/api/debug

# Frontend accesible
curl http://localhost
```

### 3. Test de conversión
- Subir un PDF pequeño
- Verificar que no aparezca error 401
- Confirmar que worker procesa la tarea

## 📋 Checklist de Verificación

- [ ] Todos los contenedores están running
- [ ] Frontend accesible en puerto 80 (via nginx)
- [ ] Backend responde en /api/debug  
- [ ] Worker logs muestran "celery ready"
- [ ] Redis conexión exitosa
- [ ] Supabase keys válidas
- [ ] Upload de PDF funciona sin 401

## 🔧 Variables de Entorno Críticas

Verificar que estas estén disponibles en los contenedores:

**Backend/Worker:**
- `FLASK_APP=app`
- `FLASK_ENV=development`  
- `SECRET_KEY=<nuevo_secret>`
- `REDIS_PASSWORD=<redis_password>`
- `SUPABASE_SECRET_KEY=sb_secret_...`
- `SUPABASE_JWT_SECRET=<jwt_secret>`

**Frontend:**
- `VITE_SUPABASE_URL=https://...`
- `VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...`

---

**Ejecutar los comandos en secuencia y verificar cada paso antes de continuar al siguiente.**