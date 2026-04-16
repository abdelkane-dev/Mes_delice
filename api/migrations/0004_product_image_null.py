# Generated migration for allowing null in image field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_contactmessage_user_order_user_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='URL de l\'image'),
        ),
    ]
