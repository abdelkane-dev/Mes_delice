import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
django.setup()

from api.models import Product, Order, OrderItem, ContactMessage
from decimal import Decimal

print("🔄 Création des données de test...")

# Supprimer les données existantes
Product.objects.all().delete()
Order.objects.all().delete()
ContactMessage.objects.all().delete()

# Créer des produits
products_data = [
    {
        'name': 'Tarte aux fraises',
        'description': 'Délicieuse tarte aux fraises fraîches sur un lit de crème pâtissière maison.',
        'price': Decimal('28.00'),
        'stock': 15,
        'category': 'gateaux',
        'image': 'https://images.unsplash.com/photo-1587668178277-295251f900ce?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Éclairs au chocolat',
        'description': 'Éclairs traditionnels garnis de crème vanille et nappés de chocolat.',
        'price': Decimal('3.50'),
        'stock': 24,
        'category': 'patisseries',
        'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Croissants pur beurre',
        'description': 'Croissants feuilletés au beurre, croustillants à l\'extérieur et moelleux.',
        'price': Decimal('1.80'),
        'stock': 36,
        'category': 'viennoiseries',
        'image': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Macarons assortis',
        'description': 'Boîte de 12 macarons aux saveurs variées: chocolat, vanille, framboise.',
        'price': Decimal('24.00'),
        'stock': 20,
        'category': 'macarons',
        'image': 'https://images.unsplash.com/photo-1569864358642-9d1684040f43?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Mille-feuille',
        'description': 'Trois couches de pâte feuilletée croustillante et crème pâtissière onctueuse.',
        'price': Decimal('5.50'),
        'stock': 12,
        'category': 'patisseries',
        'image': 'https://images.unsplash.com/photo-1464195643332-1f236b1c2255?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Tarte Tatin',
        'description': 'Tarte aux pommes caramélisées, notre recette signature.',
        'price': Decimal('22.00'),
        'stock': 8,
        'category': 'gateaux',
        'image': 'https://images.unsplash.com/photo-1519915212116-7cfef71f1d3e?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Pain au chocolat',
        'description': 'Viennoiserie feuilletée avec deux barres de chocolat noir.',
        'price': Decimal('1.50'),
        'stock': 40,
        'category': 'viennoiseries',
        'image': 'https://images.unsplash.com/photo-1623334044303-241021148842?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Forêt noire',
        'description': 'Gâteau au chocolat, chantilly et cerises, décoré de copeaux de chocolat.',
        'price': Decimal('32.00'),
        'stock': 6,
        'category': 'gateaux',
        'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Truffes au chocolat',
        'description': 'Boîte de 8 truffes artisanales au chocolat noir 70%.',
        'price': Decimal('18.00'),
        'stock': 15,
        'category': 'chocolats',
        'image': 'https://images.unsplash.com/photo-1548848928-60f3c51e8e83?w=400&h=300&fit=crop',
        'available': True
    },
    {
        'name': 'Paris-Brest',
        'description': 'Pâte à choux garnie de crème mousseline pralinée et noisettes.',
        'price': Decimal('6.50'),
        'stock': 10,
        'category': 'patisseries',
        'image': 'https://images.unsplash.com/photo-1605681187774-3d8e6e3a5883?w=400&h=300&fit=crop',
        'available': True
    },
]

print(f"📦 Création de {len(products_data)} produits...")
for product_data in products_data:
    product = Product.objects.create(**product_data)
    print(f"✅ Produit créé: {product.name}")

# Créer quelques commandes de test
print("\n📦 Création de commandes de test...")

# Commande 1
order1 = Order.objects.create(
    customer_name="Sophie Martin",
    customer_email="sophie.martin@email.com",
    customer_phone="01 23 45 67 89",
    status="pending",
    notes="Livraison avant 15h"
)
OrderItem.objects.create(
    order=order1,
    product=Product.objects.get(name="Tarte aux fraises"),
    quantity=1,
    unit_price=Product.objects.get(name="Tarte aux fraises").price
)
OrderItem.objects.create(
    order=order1,
    product=Product.objects.get(name="Macarons assortis"),
    quantity=2,
    unit_price=Product.objects.get(name="Macarons assortis").price
)
order1.calculate_total()
print(f"✅ Commande #{order1.id} créée pour {order1.customer_name}")

# Commande 2
order2 = Order.objects.create(
    customer_name="Jean Dupont",
    customer_email="jean.dupont@email.com",
    customer_phone="01 98 76 54 32",
    status="paid",
    notes=""
)
OrderItem.objects.create(
    order=order2,
    product=Product.objects.get(name="Croissants pur beurre"),
    quantity=6,
    unit_price=Product.objects.get(name="Croissants pur beurre").price
)
OrderItem.objects.create(
    order=order2,
    product=Product.objects.get(name="Pain au chocolat"),
    quantity=4,
    unit_price=Product.objects.get(name="Pain au chocolat").price
)
order2.calculate_total()
print(f"✅ Commande #{order2.id} créée pour {order2.customer_name}")

# Commande 3
order3 = Order.objects.create(
    customer_name="Marie Dubois",
    customer_email="marie.dubois@email.com",
    customer_phone="01 55 44 33 22",
    status="ready",
    notes="À retirer à 17h"
)
OrderItem.objects.create(
    order=order3,
    product=Product.objects.get(name="Forêt noire"),
    quantity=1,
    unit_price=Product.objects.get(name="Forêt noire").price
)
order3.calculate_total()
print(f"✅ Commande #{order3.id} créée pour {order3.customer_name}")

# Créer quelques messages de contact
print("\n📧 Création de messages de contact...")

messages_data = [
    {
        'name': 'Pierre Lefebvre',
        'email': 'pierre.lefebvre@email.com',
        'phone': '01 11 22 33 44',
        'subject': 'commande',
        'message': 'Bonjour, je souhaiterais commander un gâteau personnalisé pour l\'anniversaire de ma fille. Pouvez-vous me rappeler ?',
        'status': 'new'
    },
    {
        'name': 'Claire Bernard',
        'email': 'claire.bernard@email.com',
        'phone': '01 66 77 88 99',
        'subject': 'allergene',
        'message': 'Bonjour, je suis allergique aux arachides. Pourriez-vous me confirmer quels produits ne contiennent pas d\'arachides ?',
        'status': 'new'
    },
    {
        'name': 'Thomas Robert',
        'email': 'thomas.robert@email.com',
        'phone': '',
        'subject': 'renseignement',
        'message': 'Bonjour, proposez-vous des cours de pâtisserie ? Merci.',
        'status': 'read'
    },
]

for msg_data in messages_data:
    message = ContactMessage.objects.create(**msg_data)
    print(f"✅ Message de {message.name} créé")

print("\n" + "="*50)
print("🎉 Données de test créées avec succès!")
print("="*50)
print(f"\n📊 Résumé:")
print(f"   - {Product.objects.count()} produits")
print(f"   - {Order.objects.count()} commandes")
print(f"   - {OrderItem.objects.count()} articles de commande")
print(f"   - {ContactMessage.objects.count()} messages de contact")
print("\n✨ Vous pouvez maintenant tester l'application!")
print(f"   Admin: http://localhost:8000/admin/")
print(f"   API: http://localhost:8000/api/")
print(f"   Frontend: http://localhost:8000/")
