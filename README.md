# 📚 Anclora PDF2EPUB

<div align="center">

**🌍 Selecciona tu idioma / Choose your language**

[![Español](https://img.shields.io/badge/🇪🇸-Español-red?style=for-the-badge)](README.es.md)
[![English](https://img.shields.io/badge/🇺🇸-English-blue?style=for-the-badge)](README.en.md)

---

**Sistema de conversión inteligente de documentos PDF a formato EPUB3 con IA integrada**

*Intelligent PDF to EPUB3 document conversion system with integrated AI*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green.svg)](https://supabase.com/)

</div>

## 🚀 Inicio Rápido / Quick Start

### Español 🇪🇸
```bash
# Clonar el repositorio
git clone https://github.com/ToniIAPro73/Anclora-PDF2EPUB-Claude.git
cd Anclora-PDF2EPUB-Claude

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase
# Asegúrate de incluir SUPABASE_JWT_SECRET con el secreto JWT de tu proyecto

# Levantar la aplicación
docker-compose up -d

# Acceder a la aplicación
open http://localhost
```

### English 🇺🇸
```bash
# Clone the repository
git clone https://github.com/ToniIAPro73/Anclora-PDF2EPUB-Claude.git
cd Anclora-PDF2EPUB-Claude

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
# Make sure to set SUPABASE_JWT_SECRET with your project's JWT secret

# Start the application
docker-compose up -d

# Access the application
open http://localhost
```

## 📖 Documentación Completa / Full Documentation

### 🇪🇸 Documentación en Español
- **[📚 README Completo](README.es.md)** - Documentación completa en español
- **[🌍 Internacionalización](INTERNATIONALIZATION.md)** - Guía de idiomas y traducciones

### 🇺🇸 English Documentation
- **[📚 Complete README](README.en.md)** - Full documentation in English
- **[🌍 Internationalization](INTERNATIONALIZATION.md)** - Languages and translations guide

### 🌐 Agregar nuevas cadenas traducibles / Adding new translatable strings
1. Agrega la clave y su traducción en `frontend/src/locales/es.json` y `frontend/src/locales/en.json`.
2. Usa la función `t('clave')` desde `react-i18next` en los componentes React.
3. El idioma seleccionado se guarda en `localStorage` y está disponible a través de `AuthContext`.

## ✨ Características Principales / Key Features

### 🇪🇸 Español
- 🧠 **IA Integrada** - Análisis inteligente de documentos PDF
- 🚀 **3 Motores** - Rapid, Balanced y Quality para diferentes necesidades
- 📊 **Métricas** - Dashboard completo con Prometheus + Grafana
- 🌍 **Multiidioma** - Interfaz en español e inglés
- ☁️ **Cloud-Ready** - Arquitectura de microservicios escalable
- 🔐 **Supabase** - Autenticación y base de datos en la nube

### 🇺🇸 English
- 🧠 **AI-Powered** - Intelligent PDF document analysis
- 🚀 **3 Engines** - Rapid, Balanced, and Quality for different needs
- 📊 **Metrics** - Complete dashboard with Prometheus + Grafana
- 🌍 **Multilingual** - Interface in Spanish and English
- ☁️ **Cloud-Ready** - Scalable microservices architecture
- 🔐 **Supabase** - Cloud authentication and database

## 🛠️ Tecnologías / Technologies

<div align="center">

| Frontend | Backend | Database | DevOps | AI/ML |
|----------|---------|----------|--------|-------|
| React 18 | Python 3.11 | Supabase | Docker | OpenAI |
| TypeScript | Flask | PostgreSQL | Nginx | LangChain |
| Tailwind CSS | Celery | Redis | Prometheus | PDF Analysis |
| Vite | Gunicorn | - | Grafana | OCR Engine |

</div>

## 📞 Contacto / Contact

<div align="center">

**Desarrollado por / Developed by: [ToniIAPro73](https://github.com/ToniIAPro73)**

[![GitHub](https://img.shields.io/badge/GitHub-ToniIAPro73-black?style=flat&logo=github)](https://github.com/ToniIAPro73)
[![Email](https://img.shields.io/badge/Email-supertoniia@gmail.com-red?style=flat&logo=gmail)](mailto:supertoniia@gmail.com)

</div>

## 📄 Licencia / License

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**⭐ Si te gusta este proyecto, ¡dale una estrella! / If you like this project, give it a star! ⭐**

</div>
