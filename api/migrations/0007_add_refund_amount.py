# Generated migration for adding refund_amount field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_convert_prices_to_fcfa'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='refund_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                max_digits=10,
                verbose_name='Montant remboursé (FCFA)'
            ),
        ),
    ]
