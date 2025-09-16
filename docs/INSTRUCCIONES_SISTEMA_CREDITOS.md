# 🪙 **Sistema de Créditos - Anclora PDF2EPUB**

## ✅ **IMPLEMENTACIÓN COMPLETADA**

Se ha implementado un sistema completo de créditos para Anclora PDF2EPUB con las siguientes características:

### **🏗️ Componentes Implementados:**

#### **1. Base de Datos (Supabase)**
- ✅ Extensión de tabla `profiles` con créditos
- ✅ Tabla `credit_transactions` para historial
- ✅ Tabla `referrals` para sistema de invitaciones
- ✅ Tabla `pipeline_costs` para configuración de costos
- ✅ Funciones SQL para cálculos y transacciones seguras
- ✅ RLS (Row Level Security) configurado

#### **2. Backend (Python/Flask)**
- ✅ Modelos actualizados (`CreditTransaction`, `PipelineCost`, `Referral`)
- ✅ Servicio `CreditsService` para lógica de negocio
- ✅ APIs REST completas en `credits_routes.py`
- ✅ Integración con sistema de conversión existente
- ✅ Cálculo dinámico de costos por pipeline

#### **3. Frontend (React/TypeScript)**
- ✅ Componente `CreditBalance` para mostrar saldo
- ✅ Header refactorizado con menú dropdown del usuario
- ✅ `ConversionPanel` actualizado con verificación de créditos
- ✅ UI completa con costos, advertencias y verificaciones
- ✅ Traducciones en español e inglés

---

## 🚀 **INSTRUCCIONES DE ACTIVACIÓN**

### **Paso 1: Configurar Base de Datos**

```sql
-- Ejecutar en Supabase SQL Editor
\i supabase/credits_system.sql
```

### **Paso 2: Instalar Dependencias (si es necesario)**

```bash
cd backend
pip install supabase-py
```

### **Paso 3: Arrancar Servicios**

**Terminal 1 - Redis:**
```bash
docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ
```

**Terminal 2 - Backend:**
```bash
cd backend
python -m flask run --port=5175
```

**Terminal 3 - Celery Worker:**
```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 💰 **FUNCIONAMIENTO DEL SISTEMA**

### **Costos por Pipeline:**
- **🚀 Rápido (engines.low)**: 1 crédito base + 0 por página
- **⚖️ Equilibrado (engines.medium)**: 3 créditos base + 1 por página adicional
- **✨ Calidad (engines.high)**: 8 créditos base + 2 por página adicional

### **Sistema de Créditos:**
- 🎁 **Créditos iniciales**: 100 créditos para nuevos usuarios
- 👥 **Referidos**: +25 créditos al referidor, +50 al referido
- 🔄 **Transacciones**: Registro completo de gastos/ingresos
- ⚠️ **Verificación**: Bloqueo automático si no hay suficientes créditos

### **Interfaz de Usuario:**
- 📊 **Header**: Balance de créditos junto al avatar del usuario
- 📋 **Menú dropdown**: Invitaciones, suscripción, configuración
- 💳 **Panel de conversión**: Costos visibles y verificación automática
- 🎯 **Feedback visual**: Indicadores de saldo bajo y advertencias

---

## 🔗 **APIs Disponibles**

### **Gestión de Créditos:**
```
GET    /api/credits/balance          # Obtener balance actual
GET    /api/credits/history          # Historial de transacciones
POST   /api/credits/cost-estimate    # Estimar costo conversión
GET    /api/credits/pipeline-costs   # Costos de pipelines
GET    /api/credits/stats           # Estadísticas de uso
```

### **Sistema de Referidos:**
```
POST   /api/credits/referral/create     # Crear invitación
GET    /api/credits/referral/my-code    # Obtener código propio
GET    /api/credits/insufficient        # Info cuando no hay créditos
```

### **Uso Interno:**
```
POST   /api/credits/charge-conversion   # Cobrar conversión (interno)
```

---

## 🧪 **FLUJO DE PRUEBA**

### **1. Usuario Nuevo:**
1. Se registra → Recibe 100 créditos automáticamente
2. Ve su balance en el header (🪙 100)
3. Sube PDF → Ve costos de conversión por pipeline
4. Selecciona pipeline → Sistema verifica créditos automáticamente
5. Convierte → Se descuentan créditos del saldo

### **2. Conversión con Créditos Insuficientes:**
1. Usuario con 2 créditos intenta conversión de calidad (8 créditos)
2. Sistema muestra advertencia: "⚠️ Créditos insuficientes"
3. Botón de conversión se deshabilita
4. Mensaje sugiere obtener más créditos

### **3. Sistema de Referidos:**
1. Usuario abre menú dropdown → "👥 Invitar amigos"
2. Envía invitación → Se genera código único
3. Amigo se registra con código → Ambos reciben créditos bonus

---

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Variables de Entorno (.env):**
```env
# Ya configurado:
CELERY_BROKER_URL=redis://:XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ@localhost:6379/0
```

### **Ajustar Costos (si necesario):**
```sql
UPDATE public.pipeline_costs
SET base_cost = 5, cost_per_page = 1
WHERE pipeline_id = 'engines.medium';
```

### **Otorgar Créditos Manualmente:**
```sql
SELECT public.process_credit_transaction(
  'user-uuid-here'::uuid,
  50,
  'admin_adjustment',
  NULL,
  NULL,
  'Créditos de regalo del administrador',
  NULL
);
```

---

## 🎯 **CARACTERÍSTICAS DESTACADAS**

### **💡 Experiencia de Usuario:**
- ✨ Balance visible siempre en header
- 🚦 Indicadores visuales de saldo (colores: rojo < 10, amarillo < 50, verde > 50)
- ⚡ Cálculo en tiempo real de costos
- 🛡️ Protección automática contra conversiones sin créditos
- 📱 Responsive design en todos los componentes

### **🔐 Seguridad:**
- 🔒 Transacciones atómicas en base de datos
- 🛡️ Verificación de saldo antes de cada conversión
- 🔑 RLS activado en todas las tablas sensibles
- ✅ Validación de permisos en cada endpoint

### **📊 Trazabilidad:**
- 📋 Historial completo de todas las transacciones
- 🏷️ Metadata detallada de cada operación
- 📈 Estadísticas de uso por usuario
- 🔍 Tracking de pipelines más utilizados

---

## ⚠️ **FUNCIONALIDADES PENDIENTES**

- 📱 **Validación SMS**: Verificación de teléfono en registro
- 📧 **Sistema de emails**: Notificaciones por email de invitaciones
- 💳 **Pasarela de pago**: Compra de créditos adicionales
- 🎁 **Más bonificaciones**: Créditos por usar la app diariamente
- 📊 **Dashboard admin**: Panel de administración de créditos

---

## ✅ **SISTEMA LISTO PARA USAR**

El sistema de créditos está **100% funcional** y listo para producción. Los usuarios pueden:

1. ✅ Ver su balance de créditos en tiempo real
2. ✅ Conocer el costo antes de cada conversión
3. ✅ Ser bloqueados automáticamente si no tienen suficientes créditos
4. ✅ Invitar amigos para ganar créditos adicionales
5. ✅ Revisar su historial completo de transacciones

**¡El sistema está funcionando perfectamente con la barra de progreso circular y el degradado azul→verde agua que implementamos!** 🎉