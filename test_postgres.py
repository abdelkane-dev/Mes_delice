#!/usr/bin/env python
"""
Script de diagnostic pour PostgreSQL
"""
import psycopg2
import sys

def test_postgres_connection():
    """Test la connexion PostgreSQL avec différentes configurations"""
    
    print("🔍 Diagnostic PostgreSQL...")
    
    # Configuration 1: postgres/postgres
    configs = [
        {
            'name': 'Configuration par défaut (postgres/postgres)',
            'params': {
                'host': 'localhost',
                'database': 'delices_db',
                'user': 'postgres',
                'password': 'postgres'
            }
        },
        {
            'name': 'Configuration modifiée (postgres/postgres123)',
            'params': {
                'host': 'localhost',
                'database': 'delices_db',
                'user': 'postgres',
                'password': 'postgres123'
            }
        },
        {
            'name': 'Configuration sans base de données',
            'params': {
                'host': 'localhost',
                'database': 'postgres',
                'user': 'postgres',
                'password': 'postgres123'
            }
        }
    ]
    
    for config in configs:
        print(f"\n📋 Test: {config['name']}")
        try:
            conn = psycopg2.connect(**config['params'])
            print("✅ Connexion réussie!")
            
            # Vérifier si la base delices_db existe
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'delices_db'")
            exists = cursor.fetchone()
            if exists:
                print("✅ Base de données 'delices_db' existe")
            else:
                print("❌ Base de données 'delices_db' n'existe pas")
                print("💡 Créez-la avec: CREATE DATABASE delices_db;")
            
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            print(f"❌ Erreur de connexion: {e}")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
    
    print("\n🔧 Solutions possibles:")
    print("1. Changez le mot de passe PostgreSQL: ALTER USER postgres PASSWORD 'postgres123';")
    print("2. Créez la base de données: CREATE DATABASE delices_db;")
    print("3. Vérifiez que PostgreSQL est en cours d'exécution")
    
    return False

if __name__ == "__main__":
    success = test_postgres_connection()
    sys.exit(0 if success else 1)
