#!/usr/bin/env python
"""
Script de diagnostic pour Render - vérifie la configuration
"""
import os
import sys
from pathlib import Path

def check_render_config():
    """Vérifie la configuration complète de Render"""
    
    print("🔍 Diagnostic Render - Configuration complète")
    print("=" * 50)
    
    # Variables d'environnement BRUTES
    print("\n📋 Variables d'environnement BRUTES:")
    all_env = dict(os.environ)
    for key, value in all_env.items():
        if any(keyword in key.upper() for keyword in ['DATABASE', 'SECRET', 'DEBUG', 'ALLOWED', 'RENDER']):
            if 'DATABASE' in key.upper() and '@' in value:
                # Masquer le mot de passe
                parts = value.split('@')
                masked = parts[0].split(':')[-1][:4] + '***@' + parts[1]
                print(f"  {key}: postgres://****{masked}")
            else:
                print(f"  {key}: {value}")
    
    # Variables importantes
    print("\n🎯 Variables importantes:")
    env_vars = ['DATABASE_URL', 'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
    for var in env_vars:
        value = os.environ.get(var, '❌ NON DÉFINI')
        status = "✅" if os.environ.get(var) else "❌"
        print(f"  {status} {var}: {value}")
    
    # Configuration Django
    print("\n🐍 Test configuration Django:")
    try:
        # Forcer la configuration
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        print(f"  DEBUG: {settings.DEBUG}")
        print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"  DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"  DATABASE NAME: {settings.DATABASES['default'].get('NAME', 'N/A')}")
        
        # Test connexion base de données
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                print("  ✅ Connexion base de données: OK")
        except Exception as e:
            print(f"  ❌ Connexion base de données: {e}")
            
        # Test migrations
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = cursor.fetchall()
                print(f"  📊 Tables dans la base: {len(tables)}")
                for table in tables[:5]:  # Limiter à 5 tables
                    print(f"    - {table[0]}")
                if len(tables) > 5:
                    print(f"    ... et {len(tables) - 5} autres")
        except Exception as e:
            print(f"  ❌ Vérification tables: {e}")
            
    except Exception as e:
        print(f"  ❌ Erreur configuration Django: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = check_render_config()
    sys.exit(0 if success else 1)
