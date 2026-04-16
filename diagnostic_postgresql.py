#!/usr/bin/env python
"""
Script de diagnostic PostgreSQL complet
Identifie tous les problèmes potentiels de configuration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.core.management import call_command
from io import StringIO

def diagnostic_postgresql():
    """Effectue un diagnostic complet de la configuration PostgreSQL"""
    print("=" * 80)
    print("DIAGNOSTIC POSTGRESQL COMPLET")
    print("=" * 80)
    print()
    
    issues = []
    warnings = []
    
    # 1. Vérifier les variables d'environnement
    print("1️⃣  VARIABLES D'ENVIRONNEMENT")
    print("-" * 80)
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"   ✅ DATABASE_URL défini")
        print(f"      {database_url[:50]}...")
    else:
        print(f"   ℹ️  DATABASE_URL non défini (utilise configuration locale)")
        warnings.append("DATABASE_URL non défini - en mode développement local")
    
    debug = os.environ.get('DEBUG', settings.DEBUG)
    print(f"   DEBUG: {debug}")
    
    secret_key = os.environ.get('SECRET_KEY', 'non défini')
    if 'insecure' in secret_key:
        warnings.append("SECRET_KEY utilise la valeur par défaut - Changer en production!")
    print()
    
    # 2. Vérifier la configuration DATABASES
    print("2️⃣  CONFIGURATION DATABASES")
    print("-" * 80)
    
    db_config = settings.DATABASES['default']
    print(f"   ENGINE: {db_config.get('ENGINE')}")
    print(f"   NAME: {db_config.get('NAME')}")
    print(f"   USER: {db_config.get('USER')}")
    print(f"   HOST: {db_config.get('HOST')}")
    print(f"   PORT: {db_config.get('PORT')}")
    print(f"   CONN_MAX_AGE: {db_config.get('CONN_MAX_AGE')}")
    
    if db_config.get('ENGINE') != 'django.db.backends.postgresql':
        issues.append(f"⚠️  ENGINE incorrect: {db_config.get('ENGINE')}")
    else:
        print(f"   ✅ ENGINE correct (PostgreSQL)")
    print()
    
    # 3. Test de connexion
    print("3️⃣  TEST DE CONNEXION")
    print("-" * 80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   ✅ Connexion réussie")
            print(f"   PostgreSQL: {version.split(',')[0]}")
    except Exception as e:
        issues.append(f"❌ Erreur de connexion: {str(e)}")
        print(f"   ❌ Erreur: {str(e)}")
    print()
    
    # 4. Vérifier les migrations
    print("4️⃣  MIGRATIONS")
    print("-" * 80)
    
    try:
        # Capture output
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        migrations_output = out.getvalue()
        
        unapplied = migrations_output.count('[ ]')
        applied = migrations_output.count('[X]')
        
        print(f"   ✅ Migrations appliquées: {applied}")
        if unapplied > 0:
            warnings.append(f"⚠️  {unapplied} migration(s) non appliquée(s)")
            print(f"   ⚠️  Migrations non appliquées: {unapplied}")
            print(f"      Exécuter: python manage.py migrate")
        else:
            print(f"   ✅ Toutes les migrations sont appliquées")
    except Exception as e:
        issues.append(f"❌ Erreur lors de la vérification des migrations: {str(e)}")
        print(f"   ❌ Erreur: {str(e)}")
    print()
    
    # 5. Vérifier les tables
    print("5️⃣  TABLES DE LA BASE DE DONNÉES")
    print("-" * 80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'auth_user',
                'api_product',
                'api_order',
                'api_orderitem',
                'api_contactmessage',
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                issues.append(f"❌ Tables manquantes: {', '.join(missing_tables)}")
                print(f"   ❌ Tables manquantes: {', '.join(missing_tables)}")
                print(f"      Exécuter: python manage.py migrate")
            else:
                print(f"   ✅ Toutes les tables nécessaires sont présentes ({len(tables)} tables)")
    except Exception as e:
        issues.append(f"❌ Erreur lors de la vérification des tables: {str(e)}")
        print(f"   ❌ Erreur: {str(e)}")
    print()
    
    # 6. Vérifier les index
    print("6️⃣  INDEX DE LA BASE DE DONNÉES")
    print("-" * 80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """)
            indexes = cursor.fetchall()
            print(f"   ✅ {len(indexes)} index trouvés")
    except Exception as e:
        warnings.append(f"⚠️  Impossible de vérifier les index: {str(e)}")
        print(f"   ⚠️  Erreur: {str(e)}")
    print()
    
    # 7. Vérifier psycopg2
    print("7️⃣  DRIVER POSTGRESQL")
    print("-" * 80)
    
    try:
        import psycopg2
        print(f"   ✅ psycopg2 installé (version {psycopg2.__version__})")
    except ImportError:
        issues.append("❌ psycopg2 n'est pas installé")
        print(f"   ❌ psycopg2 n'est pas installé")
        print(f"      Exécuter: pip install psycopg2-binary")
    print()
    
    # 8. Vérifier dj-database-url
    print("8️⃣  DJ-DATABASE-URL")
    print("-" * 80)
    
    try:
        import dj_database_url
        print(f"   ✅ dj-database-url installé")
    except ImportError:
        issues.append("❌ dj-database-url n'est pas installé")
        print(f"   ❌ dj-database-url n'est pas installé")
        print(f"      Exécuter: pip install dj-database-url")
    print()
    
    # 9. Vérifier les permissions
    print("9️⃣  PERMISSIONS UTILISATEUR")
    print("-" * 80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    current_user AS user,
                    current_database() AS database,
                    session_user AS session_user;
            """)
            perms = cursor.fetchone()
            print(f"   Utilisateur actuel: {perms[0]}")
            print(f"   Base de données: {perms[1]}")
            print(f"   Session utilisateur: {perms[2]}")
            
            # Test de création de table temporaire
            cursor.execute("""
                CREATE TEMP TABLE test_permissions (id INT);
                DROP TABLE test_permissions;
            """)
            print(f"   ✅ Permissions CREATE/DROP validées")
    except Exception as e:
        warnings.append(f"⚠️  Problème de permissions: {str(e)}")
        print(f"   ⚠️  Erreur: {str(e)}")
    print()
    
    # 10. Résumé
    print("=" * 80)
    print("RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 80)
    print()
    
    if not issues and not warnings:
        print("✅ CONFIGURATION PARFAITE")
        print("   Aucun problème détecté.")
        print()
    else:
        if issues:
            print(f"❌ PROBLÈMES CRITIQUES ({len(issues)}):")
            for issue in issues:
                print(f"   {issue}")
            print()
        
        if warnings:
            print(f"⚠️  AVERTISSEMENTS ({len(warnings)}):")
            for warning in warnings:
                print(f"   {warning}")
            print()
    
    # Recommandations
    print("📝 ACTIONS RECOMMANDÉES:")
    print()
    
    if issues:
        print("   URGENT:")
        print("   1. Corriger les problèmes critiques listés ci-dessus")
        print("   2. python manage.py migrate")
        print("   3. python manage.py createsuperuser")
        print()
    elif warnings:
        print("   1. Examiner les avertissements")
        print("   2. python manage.py migrate (si migrations non appliquées)")
        print("   3. Lancer le serveur: python manage.py runserver")
        print()
    else:
        print("   1. python manage.py createsuperuser (si aucun utilisateur)")
        print("   2. python manage.py runserver")
        print()
    
    return len(issues) == 0

if __name__ == '__main__':
    success = diagnostic_postgresql()
    sys.exit(0 if success else 1)
