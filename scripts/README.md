# 🛠️ **Scripts de Anclora PDF2EPUB**

Este directorio contiene los scripts esenciales para el desarrollo y gestión de Anclora PDF2EPUB.

---

## 🚀 **Scripts de Desarrollo**

### **`start_dev.bat`**
**Función:** Inicia el entorno completo de desarrollo
**Servicios que arranca:**
- 🔵 Backend Flask (Puerto 5175)
- 🟢 Frontend React (Puerto 5178)
- 🔴 Redis Database (Puerto 6379)
- 🟡 Celery Worker (Conversiones)

```bash
# Uso:
scripts\start_dev.bat
```

### **`stop_dev.bat`**
**Función:** Detiene todos los servicios de desarrollo
**Lo que hace:**
- 🛑 Para Backend Flask y Celery Worker
- 🛑 Para Frontend React/Vite
- 🛑 Detiene y elimina contenedor Redis
- 🧹 Limpia archivos temporales
- ✅ Verifica que todos los puertos estén liberados

```bash
# Uso:
scripts\stop_dev.bat
```

---

## ⚙️ **Scripts de Ejecución**

### **`run-dev.bat`**
**Función:** Ejecuta el entorno de desarrollo (versión ligera)
**Para:** Desarrollo rápido sin Docker

```bash
# Uso:
scripts\run-dev.bat
```

### **`run-prod.bat`**
**Función:** Ejecuta el entorno de producción
**Para:** Testing de producción local

```bash
# Uso:
scripts\run-prod.bat
```

---

## 🔧 **Scripts de Administración**

### **`create_admin.py`**
**Función:** Crea usuarios administradores en Supabase
**Uso:** Configuración inicial del sistema

```bash
# Uso:
cd scripts
python create_admin.py
```

### **`generate-secrets.py`**
**Función:** Genera claves secretas seguras para la aplicación
**Uso:** Configuración de seguridad

```bash
# Uso:
cd scripts
python generate-secrets.py
```

---

## 📋 **Flujo de Trabajo Recomendado**

### **🚀 Inicio de desarrollo:**
```bash
# 1. Arrancar todos los servicios
scripts\start_dev.bat

# 2. Abrir navegador en http://localhost:5178
# 3. Backend disponible en http://localhost:5175
```

### **🛑 Fin de desarrollo:**
```bash
# Parar todos los servicios
scripts\stop_dev.bat
```

### **🔄 Reinicio limpio:**
```bash
scripts\stop_dev.bat
scripts\start_dev.bat
```

---

## ⚠️ **Notas Importantes**

- **Windows:** Todos los scripts están optimizados para Windows
- **Puertos:** Asegúrate de que los puertos 5175, 5178 y 6379 estén disponibles
- **Docker:** Redis requiere Docker Desktop ejecutándose
- **Dependencias:** Asegúrate de tener Python, Node.js y Docker instalados

---

## 🎯 **Troubleshooting**

### **Si los servicios no arrancan:**
1. Ejecuta `stop_dev.bat` primero
2. Verifica que Docker esté ejecutándose
3. Revisa que los puertos no estén ocupados
4. Ejecuta `start_dev.bat` de nuevo

### **Si Redis no se conecta:**
- Verifica que Docker Desktop esté ejecutándose
- El script usa Redis con contraseña configurada en `.env`

### **Si el frontend no carga:**
- Verifica que `npm install` se haya ejecutado
- Revisa que no haya errores en la consola del navegador

---

## 📁 **Estructura de Scripts**

```
scripts/
├── start_dev.bat       # ⭐ Principal - Arrancar desarrollo
├── stop_dev.bat        # ⭐ Principal - Parar desarrollo
├── run-dev.bat         # Ejecución ligera
├── run-prod.bat        # Ejecución producción
├── create_admin.py     # Crear administradores
├── generate-secrets.py # Generar secretos
└── README.md          # Esta documentación
```

---

## 🆕 **Sistema de Créditos Incluido**

Los scripts ya están configurados para funcionar con el **sistema de créditos** implementado:
- ✅ APIs de créditos disponibles
- ✅ Balance visible en header
- ✅ Verificación automática de saldo
- ✅ Cálculo de costos por pipeline

**¡Todo listo para usar!** 🎉