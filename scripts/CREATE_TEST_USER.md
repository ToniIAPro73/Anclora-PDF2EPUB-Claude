# 👤 Crear Usuario de Prueba - Post Actualización API Keys

## 🔍 Problema Identificado

El error **401 UNAUTHORIZED** ocurre porque después de actualizar las Supabase API keys (Sprint 1.2), todas las sesiones anteriores se invalidaron. El sistema está funcionando correctamente, pero necesitas autenticarte de nuevo.

## ✅ Diagnóstico Completado

- ✅ **Backend**: Funcionando, recibe las nuevas API keys
- ✅ **Frontend**: Compilando correctamente con Vite 7
- ✅ **Supabase**: Conexión exitosa con sb_publishable_ key
- ✅ **Configuración**: VITE_API_URL corregido a puerto 5175

## 🚀 Solución: Crear Usuario de Prueba

### Opción 1: Registro desde la UI
1. Ve a la página de login en tu aplicación local
2. Haz clic en "Registro" o "Sign Up"
3. Crea una cuenta con:
   - Email: `test@example.com`
   - Password: `TestPass123!`

### Opción 2: Crear usuario via Supabase Dashboard
1. Ve a [Supabase Dashboard](https://supabase.com/dashboard)
2. Proyecto: kehpwxdkpdxapfxwhfwn
3. Authentication → Users → Add User
4. Email: `test@example.com`
5. Password: `TestPass123!`
6. Confirmar email automáticamente

### Opción 3: Script de creación (Recomendado)
```bash
# Desde el directorio del proyecto
cd backend
python scripts/create-test-user.py
```

## 🧪 Testing Post-Autenticación

Una vez logueado, prueba:

1. **Upload de PDF**: Debería funcionar sin error 401
2. **Conversión**: Worker debería procesar el archivo
3. **Historial**: Ver conversiones previas
4. **Logout/Login**: Verificar que las sesiones persisten

## 🔧 Comandos de Verificación

### Verificar estado de auth en frontend
```javascript
// En la consola del navegador
window.localStorage.getItem('supabase.auth.token')
```

### Verificar conexión backend
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5175/api/convert
```

### Verificar configuración Supabase
```bash
cd frontend && node test-supabase.js
```

## ⚠️ Si el registro falla

### Revisar configuración de email en Supabase:
1. Dashboard → Authentication → Settings
2. **Email confirmations**: Disable para testing
3. **Email change confirmations**: Disable para testing

### Verificar RLS (Row Level Security):
1. Dashboard → Table Editor → conversions
2. Verificar que RLS policies permitan insert/select

## 📋 Checklist de Verificación

- [ ] Usuario creado exitosamente
- [ ] Login funciona sin errores
- [ ] Token de auth se genera correctamente
- [ ] Upload de PDF funciona (no más 401)
- [ ] Conversión se procesa correctamente
- [ ] Logout/Login preserva funcionalidad

## 🎯 Resultado Esperado

Después de crear y loguearte con el usuario de prueba:
- ✅ **Error 401**: Resuelto
- ✅ **Conversión PDF**: Funcional
- ✅ **Autenticación**: Trabajando con new API keys
- ✅ **Sistema completo**: Operacional

---

**El problema no es técnico sino de estado de sesión. Todo está funcionando correctamente tras las actualizaciones de seguridad.**