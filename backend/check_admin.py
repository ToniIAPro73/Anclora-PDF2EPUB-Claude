#!/usr/bin/env python3
"""
Script para verificar el usuario admin y su contraseña
"""
import os
import sys
from werkzeug.security import check_password_hash

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app.models import User

def check_admin_user():
    """Verificar usuario administrador"""
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Buscar usuario admin
        user = db.query(User).filter(User.username == 'admin').first()
        
        if not user:
            print("❌ Usuario admin no encontrado")
            return
        
        print("✅ Usuario admin encontrado:")
        print(f"👤 ID: {user.id}")
        print(f"👤 Username: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔒 Password hash: {user.password[:50]}...")
        print(f"✅ Is active: {user.is_active}")
        print(f"📅 Created at: {user.created_at}")
        
        # Verificar contraseña
        password_test = 'admin123'
        is_valid = check_password_hash(user.password, password_test)
        
        print(f"\n🔑 Verificación de contraseña '{password_test}': {'✅ VÁLIDA' if is_valid else '❌ INVÁLIDA'}")
        
        if not is_valid:
            print("🔧 Intentando otras contraseñas comunes...")
            for pwd in ['admin', 'password', '123456', 'admin1234']:
                if check_password_hash(user.password, pwd):
                    print(f"✅ Contraseña correcta encontrada: '{pwd}'")
                    return
            print("❌ Ninguna contraseña común funciona")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()
