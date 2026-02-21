# Generated migration for converting prices from EUR to FCFA

from django.db import migrations

def convert_prices_to_fcfa(apps, schema_editor):
    """
    Convert all prices from EUR to FCFA (multiply by 655)
    """
    Product = apps.get_model('api', 'Product')
    Order = apps.get_model('api', 'Order')
    OrderItem = apps.get_model('api', 'OrderItem')
    
    # Convert product prices
    for product in Product.objects.all():
        product.price = product.price * 655
        product.save()
    
    # Convert order total prices
    for order in Order.objects.all():
        order.total_price = order.total_price * 655
        order.save()
    
    # Convert order item prices
    for item in OrderItem.objects.all():
        item.unit_price = item.unit_price * 655
        item.save()

def convert_prices_to_eur(apps, schema_editor):
    """
    Reverse migration: convert FCFA back to EUR (divide by 655)
    """
    Product = apps.get_model('api', 'Product')
    Order = apps.get_model('api', 'Order')
    OrderItem = apps.get_model('api', 'OrderItem')
    
    # Convert product prices back
    for product in Product.objects.all():
        product.price = product.price / 655
        product.save()
    
    # Convert order total prices back
    for order in Order.objects.all():
        order.total_price = order.total_price / 655
        order.save()
    
    # Convert order item prices back
    for item in OrderItem.objects.all():
        item.unit_price = item.unit_price / 655
        item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_product_image_alter_product_price'),
    ]

    operations = [
        migrations.RunPython(convert_prices_to_fcfa, convert_prices_to_eur),
    ]
