#!/usr/bin/env python3
"""
Script para crear el usuario administrador inicial
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db, init_db
from app.models import User

def create_admin_user():
    """Crear usuario administrador inicial"""
    
    # Inicializar base de datos
    print("🔧 Inicializando base de datos...")
    init_db()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Verificar si el usuario admin ya existe
        existing_user = db.query(User).filter(User.username == 'admin').first()
        
        if existing_user:
            print("ℹ️  Usuario admin ya existe")
            print(f"👤 Username: {existing_user.username}")
            print(f"📧 Email: {existing_user.email}")
            return
        
        # Crear usuario admin
        print("👤 Creando usuario administrador...")
        hashed_password = generate_password_hash('admin123')
        
        admin_user = User(
            username='admin',
            email='admin@anclora.com',
            password=hashed_password,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuario admin creado exitosamente!")
        print(f"👤 Username: admin")
        print(f"🔑 Password: admin123")
        print(f"📧 Email: admin@anclora.com")
        print(f"🆔 ID: {admin_user.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
