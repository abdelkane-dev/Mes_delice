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
    
    # Variables d'environnement
    print("\n📋 Variables d'environnement:")
    env_vars = ['DATABASE_URL', 'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
    for var in env_vars:
        value = os.environ.get(var, 'NON DÉFINI')
        if var == 'DATABASE_URL':
            # Masquer le mot de passe
            if '@' in value:
                parts = value.split('@')
                masked = parts[0].split(':')[-1][:4] + '***@' + parts[1]
                print(f"  {var}: postgres://****{masked}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: {value}")
    
    # Configuration Django
    print("\n🐍 Test configuration Django:")
    try:
        import django
        from django.conf import settings
        
        print(f"  DEBUG: {settings.DEBUG}")
        print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"  DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"  DATABASE NAME: {settings.DATABASES['default']['NAME']}")
        
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
            from django.core.management import execute_from_command_line
            from django.core.management.commands.showmigrations import Command as ShowMigrations
            # Vérifier si les tables existent
            with connection.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = cursor.fetchall()
                print(f"  📊 Tables dans la base: {len(tables)}")
                for table in tables:
                    print(f"    - {table[0]}")
        except Exception as e:
            print(f"  ❌ Vérification tables: {e}")
            
    except Exception as e:
        print(f"  ❌ Erreur configuration Django: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_render_config()
    sys.exit(0 if success else 1)
