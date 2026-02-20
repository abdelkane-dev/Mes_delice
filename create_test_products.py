import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
django.setup()

from api.models import Product

# Supprimer les anciens produits de test
Product.objects.all().delete()

# Créer des produits de test
products = [
    {
        'name': 'Tarte aux Fraises',
        'description': 'Une délicieuse tarte aux fraises fraîches sur une base de pâte sablée',
        'price': 18.50,
        'stock': 10,
        'category': 'gateaux',
        'available': True
    },
    {
        'name': 'Éclair au Chocolat',
        'description': 'Éclair traditionnel fourré à la crème pâtissière au chocolat',
        'price': 4.50,
        'stock': 25,
        'category': 'patisseries',
        'available': True
    },
    {
        'name': 'Croissant au Beurre',
        'description': 'Croissant artisanal au beurre AOP, croustillant et doré',
        'price': 1.50,
        'stock': 50,
        'category': 'viennoiseries',
        'available': True
    },
    {
        'name': 'Macaron Pistache',
        'description': 'Macaron délicat à la pistache de Sicile',
        'price': 2.80,
        'stock': 30,
        'category': 'macarons',
        'available': True
    },
    {
        'name': 'Truffes au Chocolat',
        'description': 'Truffes artisanales au chocolat noir 70%',
        'price': 15.00,
        'stock': 0,  # Rupture de stock
        'category': 'chocolats',
        'available': False
    }
]

for product_data in products:
    product = Product.objects.create(**product_data)
    print(f"✅ Produit créé : {product.name} - {product.price}€ (stock: {product.stock})")

print(f"\n✅ {Product.objects.count()} produits créés avec succès!")
