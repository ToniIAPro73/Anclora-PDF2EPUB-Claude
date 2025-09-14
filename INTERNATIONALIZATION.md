# 🌍 Internacionalización (i18n) - Anclora PDF2EPUB

## Descripción

La aplicación Anclora PDF2EPUB ahora cuenta con soporte completo para múltiples idiomas, permitiendo a los usuarios cambiar entre **Español** e **Inglés** de forma dinámica.

## 🚀 Características

### ✅ Idiomas Soportados
- **🇪🇸 Español** (idioma por defecto)
- **🇺🇸 English** (inglés)

### ✅ Funcionalidades
- **Cambio dinámico de idioma** sin necesidad de recargar la página
- **Persistencia de preferencia** en localStorage del navegador
- **Detección automática** del idioma del navegador
- **Selector visual** con banderas y nombres de idiomas
- **Traducción completa** de toda la interfaz de usuario

## 🛠️ Implementación Técnica

### Dependencias Instaladas
```bash
npm install react-i18next i18next i18next-browser-languagedetector
```

### Estructura de Archivos
```
frontend/src/
├── i18n/
│   ├── index.ts              # Configuración principal de i18n
│   └── locales/
│       ├── es.json           # Traducciones en español
│       └── en.json           # Traducciones en inglés
└── components/
    └── LanguageSelector.tsx  # Componente selector de idioma
```

### Configuración
- **Idioma por defecto**: Español (`es`)
- **Fallback**: Español si no se encuentra traducción
- **Detección**: localStorage > navegador > HTML tag
- **Cache**: localStorage para persistencia

## 🎯 Componentes Traducidos

### ✅ Páginas Principales
- **Página de inicio** con hero section y características
- **Formulario de login** con todos los campos y mensajes
- **Formulario de registro** con validaciones
- **Historial de conversiones** con estados y acciones

### ✅ Componentes de UI
- **Header/Navegación** con menús y botones
- **FileUploader** con mensajes de error y estado
- **Selector de idioma** con dropdown interactivo
- **Botones de tema** (claro/oscuro)

### ✅ Mensajes del Sistema
- **Errores de autenticación** y validación
- **Estados de carga** y procesamiento
- **Mensajes de éxito** y confirmación
- **Textos de ayuda** y descripciones

## 🎨 Selector de Idioma

### Características del Componente
- **Dropdown elegante** con animaciones suaves
- **Banderas visuales** para identificación rápida
- **Indicador de idioma activo** con checkmark
- **Cierre automático** al hacer clic fuera
- **Responsive** para dispositivos móviles

### Ubicaciones
- **Header principal** (aplicación logueada)
- **Página de login** (esquina superior derecha)
- **Página de registro** (esquina superior derecha)

## 📝 Estructura de Traducciones

### Organización JSON
```json
{
  "app": {
    "title": "Anclora PDF2EPUB",
    "subtitle": "Conversión inteligente de PDF a EPUB3"
  },
  "navigation": {
    "home": "Inicio",
    "history": "Historial",
    "logout": "Cerrar Sesión"
  },
  "auth": {
    "login": "Iniciar Sesión",
    "email": "Correo Electrónico",
    "password": "Contraseña"
  }
}
```

### Uso en Componentes
```typescript
import { useTranslation } from 'react-i18next';

const Component = () => {
  const { t } = useTranslation();
  
  return (
    <h1>{t('app.title')}</h1>
  );
};
```

## 🔧 Cómo Agregar Nuevos Idiomas

### 1. Crear archivo de traducción
```bash
# Crear nuevo archivo de idioma
touch frontend/src/i18n/locales/fr.json
```

### 2. Agregar traducciones
```json
{
  "app": {
    "title": "Anclora PDF2EPUB",
    "subtitle": "Conversion intelligente de PDF vers EPUB3"
  }
}
```

### 3. Actualizar configuración
```typescript
// En frontend/src/i18n/index.ts
import fr from './locales/fr.json';

const resources = {
  es: { translation: es },
  en: { translation: en },
  fr: { translation: fr }  // Nuevo idioma
};
```

### 4. Actualizar selector
```typescript
// En LanguageSelector.tsx
const languages = [
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' }  // Nuevo idioma
];
```

## 🚀 Uso para Desarrolladores

### Obtener traducción
```typescript
const { t } = useTranslation();
const title = t('app.title');
```

### Cambiar idioma programáticamente
```typescript
const { i18n } = useTranslation();
i18n.changeLanguage('en');
```

### Obtener idioma actual
```typescript
const { i18n } = useTranslation();
const currentLanguage = i18n.language;
```

## 🎉 Beneficios

### Para Usuarios
- **Experiencia personalizada** en su idioma nativo
- **Interfaz familiar** y fácil de usar
- **Accesibilidad mejorada** para usuarios internacionales

### Para Desarrolladores
- **Código mantenible** con traducciones centralizadas
- **Escalabilidad** para agregar nuevos idiomas fácilmente
- **Consistencia** en toda la aplicación

### Para el Negocio
- **Alcance global** expandido
- **Mejor experiencia de usuario** internacional
- **Competitividad** en mercados internacionales

## 🔄 Estado Actual

✅ **Implementación completa** de español e inglés
✅ **Todos los componentes** traducidos
✅ **Selector funcional** en todas las páginas
✅ **Persistencia** de preferencias
✅ **Detección automática** del idioma

¡La aplicación está lista para usuarios de habla hispana e inglesa! 🎊
