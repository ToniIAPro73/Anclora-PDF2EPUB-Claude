# Configuración de Docker para Anclora PDF2EPUB

## Problema Resuelto

Se ha solucionado el problema donde el cambio de idioma no funcionaba correctamente cuando el frontend se ejecutaba desde Docker, pero sí funcionaba cuando se ejecutaba localmente con `npm start`.

## Causa del Problema

El problema se debía a que:
1. **Docker usaba modo producción**: El Dockerfile original construía la aplicación (`npm run build`) y la servía con `vite preview`, que sirve archivos estáticos.
2. **Desarrollo local usaba modo desarrollo**: `npm start` ejecuta `vite` en modo desarrollo con hot reloading y mejor manejo de cambios dinámicos.
3. **Diferencias en el manejo de estado**: El modo preview no maneja tan bien los cambios dinámicos de estado como el modo desarrollo.

## Solución Implementada

### 1. Dockerfiles Separados
- **`docker/Dockerfile.frontend`**: Para desarrollo (usa `npm start`)
- **`docker/Dockerfile.frontend.prod`**: Para producción (usa `npm run build` + `npm run serve`)

### 2. Docker Compose Separados
- **`docker-compose.dev.yml`**: Para desarrollo
- **`docker-compose.yml`**: Para producción

### 3. Mejoras en el Código
- **Variables de entorno**: Soporte para `VITE_*` además de `REACT_APP_*`
- **Forzar re-render**: Agregado `useEffect` en `FileUploader` para forzar actualización cuando cambia el idioma
- **Configuración i18n mejorada**: Mejor configuración para compatibilidad entre modos

## Uso

### Para Desarrollo (Recomendado)
```bash
# Usar el docker-compose de desarrollo
docker-compose -f docker-compose.dev.yml up --build

# O para reconstruir solo el frontend
docker-compose -f docker-compose.dev.yml up --build frontend
```

### Para Producción
```bash
# Usar el docker-compose normal
docker-compose up --build
```

### Desarrollo Local (Sin Docker)
```bash
cd frontend
npm start
# Se ejecutará en puerto 5178 (o 5179 si 5178 está ocupado por Docker)
```

### Ejecución Simultánea
Puedes ejecutar tanto Docker como desarrollo local al mismo tiempo:
- **Docker**: http://localhost (nginx) o http://localhost:5178 (directo)
- **Local**: http://localhost:5179 (Vite auto-incrementa el puerto si 5178 está ocupado)

## Puertos Configurados

- **Frontend**: 5178 (cambiado desde 3003)
- **Backend**: 5175
- **Nginx**: 80
- **Redis**: 6379

## Variables de Entorno

El sistema ahora soporta tanto variables `VITE_*` como `REACT_APP_*`:

```env
# En .env o .env.local
VITE_API_URL=http://localhost/api
VITE_SUPABASE_URL=https://kehpwxdkpdxapfxwhfwn.supabase.co
VITE_SUPABASE_ANON_KEY=...
```

## Verificación

Para verificar que el cambio de idioma funciona:

1. Ejecutar con Docker: `docker-compose -f docker-compose.dev.yml up --build`
2. Abrir http://localhost
3. Cambiar idioma en el selector
4. Verificar que el área de subida de PDF cambia de idioma inmediatamente

## Archivos Modificados

- `docker/Dockerfile.frontend` - Cambiado a modo desarrollo
- `docker/Dockerfile.frontend.prod` - Nuevo, para producción
- `docker-compose.dev.yml` - Nuevo, para desarrollo
- `docker-compose.yml` - Actualizado para producción
- `frontend/vite.config.js` - Mejorada configuración
- `frontend/src/i18n/index.ts` - Configuración i18n mejorada
- `frontend/src/components/FileUploader.tsx` - Forzar re-render en cambio de idioma
- `.env` - Puerto cambiado a 5178
- `docker/nginx/nginx.conf` - Puerto actualizado
