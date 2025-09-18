# Anclora PDF2EPUB

## Overview

Anclora PDF2EPUB is an intelligent PDF to EPUB3 document conversion system with integrated AI analysis. The application provides enterprise-grade document conversion through multiple specialized engines optimized for different content types. It features a microservices architecture with a React/TypeScript frontend, Flask/Python backend, and asynchronous task processing with Celery. The system includes comprehensive user authentication, credit management, conversion history tracking, and multilingual support (Spanish and English).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18.2.0 with TypeScript 5.2+
- **Build System**: Vite 7.1.5 with ESBuild integration
- **UI Framework**: Tailwind CSS for responsive design with dark/light theme support
- **State Management**: Component-level state with hooks, no global state management library
- **Internationalization**: i18next with browser language detection and localStorage persistence
- **File Handling**: React Dropzone for drag-and-drop PDF uploads with real-time validation
- **Security**: DOMPurify for HTML sanitization to prevent XSS attacks
- **Animation**: Lottie integration for loading animations during file processing

### Backend Architecture
- **Framework**: Flask 3.0.3 with modular blueprint structure
- **Database**: PostgreSQL with SQLAlchemy ORM for local data + Supabase for user management
- **Task Queue**: Celery 5.5.3 with Redis 6.1.1 for asynchronous PDF conversion processing
- **Authentication**: Dual system - JWT tokens for local auth + Supabase Auth integration
- **File Processing**: Multiple conversion engines (Rapid, Balanced, Quality) using PyMuPDF, Pandoc, and OCR
- **Security**: Flask-Limiter for rate limiting, comprehensive file validation with magic number checks
- **Monitoring**: Prometheus metrics integration for performance tracking

### Conversion Engine Design
The system implements three specialized conversion pipelines:
- **Rapid Engine**: For simple text-only documents (2-5 seconds)
- **Balanced Engine**: For mixed text and image documents (10-30 seconds)  
- **Quality Engine**: For complex documents with OCR processing (30-120 seconds)

Each engine includes AI-powered content analysis to detect document complexity, language, tables, and mathematical formulas to recommend the optimal conversion approach.

### Database Design
- **Local SQLAlchemy Models**: Conversion tracking, user management, credit transactions
- **Supabase Integration**: User profiles, authentication, and credit management with Row Level Security
- **File Storage**: Local filesystem for temporary processing with configurable cleanup policies

### Credit System Architecture
Implements a comprehensive credit-based usage system with:
- Per-conversion credit deduction based on pipeline complexity and document size
- Transaction history tracking with audit trails
- Referral system for credit bonuses
- Configurable pipeline costs stored in database

## External Dependencies

### Core Services
- **Supabase**: Primary authentication provider and user profile management
- **Redis**: Task queue backend and caching layer (password: `XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ`)
- **PostgreSQL**: Primary database for conversion tracking and local data storage

### PDF Processing Libraries
- **PyMuPDF (fitz)**: Core PDF reading and manipulation
- **EbookLib**: EPUB creation and validation
- **Pandoc**: Document format conversion engine
- **pdf2htmlEX**: Advanced PDF to HTML conversion
- **Tesseract OCR**: Optical character recognition for scanned documents
- **Camelot**: Table extraction from PDF documents

### Infrastructure & Monitoring
- **Docker Compose**: Multi-service containerization for development and production
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization dashboard
- **Flask-CORS**: Cross-origin request handling for API endpoints

### Security & Validation
- **python-magic**: File type validation through magic numbers
- **Werkzeug Security**: Password hashing and security utilities
- **Flask-Limiter**: API rate limiting and abuse prevention
- **DOMPurify**: Frontend HTML sanitization for XSS prevention

### Development Tools
- **Celery**: Distributed task queue for background processing
- **Alembic**: Database migration management
- **pytest**: Testing framework for backend components
- **Vite**: Frontend build tool and development server