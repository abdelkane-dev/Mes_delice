# Script pour appliquer la migration manuellement
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
django.setup()

from django.db import connection

# Appliquer la modification manuellement du schéma
with connection.cursor() as cursor:
    # Créer une table temporaire avec la nouvelle structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_product_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            slug VARCHAR(200) UNIQUE NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock INTEGER NOT NULL,
            available BOOLEAN NOT NULL DEFAULT 1,
            category VARCHAR(20) NOT NULL DEFAULT 'patisseries',
            image VARCHAR(500) NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    ''')
    
    # Copier les données
    cursor.execute('''
        INSERT INTO api_product_new (
            id, name, slug, description, price, stock, 
            available, category, image, created_at, updated_at
        )
        SELECT 
            id, name, slug, description, price, stock,
            available, category, image, created_at, updated_at
        FROM api_product
    ''')
    
    # Supprimer l'ancienne table
    cursor.execute('DROP TABLE api_product')
    
    # Renommer la nouvelle table
    cursor.execute('ALTER TABLE api_product_new RENAME TO api_product')

print("Migration appliquée avec succès !")
