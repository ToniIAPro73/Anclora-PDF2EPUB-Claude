# 🐍 Guía Entorno Virtual Python (PowerShell, CMD y Bash)

## 🚀 Inicio Rápido con Entorno Virtual

### 1. Configurar Todo Automáticamente
```powershell
# Ejecutar script que configura Redis + verifica venv
scripts\setup_hybrid_dev_venv.bat
```

### 2. Activar Entorno Virtual

#### PowerShell
```powershell
# Activar entorno virtual Python
.\venv-py311\Scripts\Activate.ps1

# Verificar que está activo (debe mostrar (venv-py311) al inicio)
# (venv-py311) PS C:\...\Anclora-PDF2EPUB-Claude>
```

#### Git Bash / WSL / Linux Terminal
```bash
# Activar entorno virtual Python
source venv-py311/Scripts/activate

# En Linux/Mac sería:
# source venv-py311/bin/activate

# Verificar que está activo (debe mostrar (venv-py311) al inicio)
# (venv-py311) $
```

#### Command Prompt (CMD)
```cmd
# Activar entorno virtual Python
venv-py311\Scripts\activate.bat

# Verificar que está activo
# (venv-py311) C:\...\Anclora-PDF2EPUB-Claude>
```

### 3. Ejecutar Backend (Terminal con venv activo)
```bash
# Con el entorno virtual activado (cualquier terminal)
cd backend
pip install -r requirements.txt
python main.py
```

### 4. Ejecutar Frontend (Nueva terminal - sin venv)
```bash
# En nueva terminal (cualquier tipo)
cd frontend
npm install
npm start
```

### 5. Ejecutar Celery Worker (Terminal con venv activo)
```bash
# Con el entorno virtual activado (cualquier terminal)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet
```

## 🔧 Comandos Útiles

### Activación/Desactivación

#### PowerShell
```powershell
# ACTIVAR (en raíz del proyecto)
.\venv-py311\Scripts\Activate.ps1

# DESACTIVAR (desde cualquier lugar)
deactivate

# Verificar Python en uso
where python
# Debe mostrar: C:\...\venv-py311\Scripts\python.exe
```

#### Git Bash / WSL
```bash
# ACTIVAR (en raíz del proyecto)
source venv-py311/Scripts/activate

# DESACTIVAR (desde cualquier lugar)
deactivate

# Verificar Python en uso
which python
# Debe mostrar: /c/.../venv-py311/Scripts/python.exe
```

#### Command Prompt (CMD)
```cmd
# ACTIVAR (en raíz del proyecto)
venv-py311\Scripts\activate.bat

# DESACTIVAR (desde cualquier lugar)
deactivate

# Verificar Python en uso
where python
```

### Gestión de Paquetes
```powershell
# Con venv activado
pip list                    # Ver paquetes instalados
pip install paquete         # Instalar nuevo paquete
pip freeze > requirements.txt  # Actualizar requirements
```

## ⚠️ Problemas Comunes en PowerShell

### Error de Ejecución de Scripts
```powershell
# Si PowerShell bloquea la activación del venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego intentar activar de nuevo
.\venv-py311\Scripts\Activate.ps1
```

### Alternativa con CMD
Si PowerShell da problemas, usar Command Prompt:
```cmd
# Activar en CMD
venv-py311\Scripts\activate.bat

# Continuar con los mismos pasos
cd backend
pip install -r requirements.txt
python main.py
```

## 🎯 Flujo de Desarrollo Completo

### Terminal 1 - Redis (cualquier terminal)
```powershell
scripts\setup_hybrid_dev_venv.bat
```

### Terminal 2 - Backend (con venv)
#### PowerShell
```powershell
.\venv-py311\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
python main.py
```

#### Git Bash
```bash
source venv-py311/Scripts/activate
cd backend
pip install -r requirements.txt
python main.py
```

### Terminal 3 - Frontend (sin venv)
```bash
cd frontend
npm install
npm start
```

### Terminal 4 - Celery (con venv)
#### PowerShell
```powershell
.\venv-py311\Scripts\Activate.ps1
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet
```

#### Git Bash
```bash
source venv-py311/Scripts/activate
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet
```

## 📍 URLs Finales
- **Frontend**: http://localhost:5178
- **Backend**: http://localhost:5175
- **Redis**: localhost:6379

## 🛑 Detener Todo
```powershell
# Detener Redis
docker stop redis-anclora

# Desactivar venv en terminals backend/celery
deactivate

# Ctrl+C en cada terminal para backend/frontend/celery
```

## 💡 Ventajas del Entorno Virtual

- ✅ **Aislamiento**: Paquetes separados del Python del sistema
- ✅ **Reproducibilidad**: Mismas versiones en todos los entornos
- ✅ **Sin conflictos**: No afecta otros proyectos Python
- ✅ **Limpio**: Fácil de eliminar y recrear si se corrompe

---
**¡Ya puedes desarrollar con entorno virtual limpio y aislado!**