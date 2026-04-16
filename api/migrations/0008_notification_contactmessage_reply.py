from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0007_add_refund_amount'),
    ]

    operations = [
        # Ajouter les champs de réponse au modèle ContactMessage
        migrations.AddField(
            model_name='contactmessage',
            name='admin_reponse',
            field=models.TextField(blank=True, null=True, verbose_name='Réponse de l\'admin'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='repondu_le',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Répondu le'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='repondu_par',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='messages_repondus',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Répondu par',
            ),
        ),
        # Créer la table notifications
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(
                    max_length=50,
                    choices=[
                        ('nouvelle_commande', 'Nouvelle commande'),
                        ('commande_annulee', 'Commande annulée'),
                        ('commande_prete', 'Commande prête'),
                        ('commande_livree', 'Commande livrée'),
                        ('commande_statut', 'Statut de commande'),
                        ('reponse_message', 'Réponse à un message'),
                        ('nouveau_message', 'Nouveau message contact'),
                    ],
                    verbose_name='Type',
                )),
                ('message', models.TextField(verbose_name='Message')),
                ('lien', models.CharField(blank=True, max_length=255, null=True, verbose_name='Lien')),
                ('est_lue', models.BooleanField(default=False, verbose_name='Est lue')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créée le')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
    ]
