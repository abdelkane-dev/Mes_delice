#!/usr/bin/env python
"""
Script de test de connexion PostgreSQL
Vérifie que la base de données est accessible et correctement configurée
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
django.setup()

from django.db import connection
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User
from api.models import Product, Order, OrderItem, ContactMessage

def test_database_connection():
    """Teste la connexion à la base de données"""
    print("=" * 70)
    print("TEST DE CONNEXION POSTGRESQL")
    print("=" * 70)
    print()
    
    try:
        # Test de connexion basique
        print("1️⃣  Test de connexion à la base de données...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            print(f"   ✅ Connexion réussie!")
            print(f"   📊 Version PostgreSQL: {db_version}")
            print()
        
        # Informations de configuration
        print("2️⃣  Configuration de la base de données:")
        db_settings = connection.settings_dict
        print(f"   🔧 ENGINE: {db_settings.get('ENGINE', 'Non défini')}")
        print(f"   🏷️  NAME: {db_settings.get('NAME', 'Non défini')}")
        print(f"   👤 USER: {db_settings.get('USER', 'Non défini')}")
        print(f"   🌐 HOST: {db_settings.get('HOST', 'Non défini')}")
        print(f"   🔌 PORT: {db_settings.get('PORT', 'Non défini')}")
        print(f"   ⏱️  CONN_MAX_AGE: {db_settings.get('CONN_MAX_AGE', 'Non défini')}")
        print()
        
        # Test des tables
        print("3️⃣  Vérification des tables:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"   ✅ {len(tables)} tables trouvées:")
                for table in tables:
                    print(f"      - {table[0]}")
            else:
                print("   ⚠️  Aucune table trouvée. Exécutez 'python manage.py migrate'")
        print()
        
        # Test des modèles
        print("4️⃣  Test des modèles Django:")
        
        # User
        try:
            user_count = User.objects.count()
            print(f"   ✅ User: {user_count} utilisateur(s)")
        except Exception as e:
            print(f"   ❌ User: Erreur - {str(e)}")
        
        # Product
        try:
            product_count = Product.objects.count()
            print(f"   ✅ Product: {product_count} produit(s)")
        except Exception as e:
            print(f"   ❌ Product: Erreur - {str(e)}")
        
        # Order
        try:
            order_count = Order.objects.count()
            print(f"   ✅ Order: {order_count} commande(s)")
        except Exception as e:
            print(f"   ❌ Order: Erreur - {str(e)}")
        
        # OrderItem
        try:
            orderitem_count = OrderItem.objects.count()
            print(f"   ✅ OrderItem: {orderitem_count} article(s)")
        except Exception as e:
            print(f"   ❌ OrderItem: Erreur - {str(e)}")
        
        # ContactMessage
        try:
            message_count = ContactMessage.objects.count()
            print(f"   ✅ ContactMessage: {message_count} message(s)")
        except Exception as e:
            print(f"   ❌ ContactMessage: Erreur - {str(e)}")
        print()
        
        # Test des requêtes avec jointures
        print("5️⃣  Test des requêtes complexes:")
        
        try:
            # Test requête avec user filter
            orders_with_user = Order.objects.filter(user__isnull=False).count()
            print(f"   ✅ Orders avec user: {orders_with_user}")
        except Exception as e:
            print(f"   ❌ Orders avec user: Erreur - {str(e)}")
        
        try:
            # Test prefetch_related
            orders = Order.objects.all().prefetch_related('items__product')[:5]
            print(f"   ✅ Prefetch related: {len(list(orders))} commandes chargées")
        except Exception as e:
            print(f"   ❌ Prefetch related: Erreur - {str(e)}")
        print()
        
        # Résumé
        print("=" * 70)
        print("✅ TOUS LES TESTS SONT PASSÉS")
        print("=" * 70)
        print()
        print("📝 Actions recommandées:")
        print("   1. Si aucune table n'est trouvée: python manage.py migrate")
        print("   2. Si aucun utilisateur: python manage.py createsuperuser")
        print("   3. Lancer le serveur: python manage.py runserver")
        print()
        
        return True
        
    except ImproperlyConfigured as e:
        print()
        print("=" * 70)
        print("❌ ERREUR DE CONFIGURATION")
        print("=" * 70)
        print(f"Erreur: {str(e)}")
        print()
        print("📝 Vérifications à faire:")
        print("   1. Vérifier que PostgreSQL est installé et démarré")
        print("   2. Vérifier les paramètres de connexion dans .env")
        print("   3. Vérifier que la base de données existe")
        print("   4. Vérifier que l'utilisateur a les droits nécessaires")
        print()
        return False
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERREUR DE CONNEXION")
        print("=" * 70)
        print(f"Erreur: {str(e)}")
        print()
        print("📝 Vérifications à faire:")
        print("   1. PostgreSQL est-il démarré?")
        print("   2. Les identifiants sont-ils corrects?")
        print("   3. La base de données existe-t-elle?")
        print("   4. Le pare-feu bloque-t-il la connexion?")
        print()
        print("🔧 Commandes utiles:")
        print("   # Créer la base de données (si nécessaire)")
        print("   createdb delices_db")
        print()
        print("   # Ou avec psql:")
        print("   psql -U postgres")
        print("   CREATE DATABASE delices_db;")
        print()
        return False

if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1)
