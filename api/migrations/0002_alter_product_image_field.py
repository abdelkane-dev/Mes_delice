# Generated migration for changing image field from URLField to TextField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.TextField(blank=True, verbose_name='Image (URL ou base64)'),
        ),
    ]
