from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Product(models.Model):
    """Modèle pour les produits de la pâtisserie"""
    
    CATEGORY_CHOICES = [
        ('gateaux', 'Gâteaux'),
        ('patisseries', 'Pâtisseries'),
        ('viennoiseries', 'Viennoiseries'),
        ('macarons', 'Macarons'),
        ('chocolats', 'Chocolats'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix (€)"
    )
    stock = models.PositiveIntegerField(
        default=0, 
        verbose_name="Stock disponible"
    )
    available = models.BooleanField(
        default=True, 
        verbose_name="Produit disponible"
    )
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        default='patisseries',
        verbose_name="Catégorie"
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Image du produit"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Date de mise à jour"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le slug si non défini"""
        if not self.slug:
            import re
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock > 0 and self.available
    
    @property
    def stock_status(self):
        """Retourne le statut du stock"""
        if not self.available:
            return 'non disponible'
        elif self.stock == 0:
            return 'rupture'
        elif self.stock <= 5:
            return 'stock faible'
        else:
            return 'en stock'
    
    def decrease_stock(self, quantity):
        """Diminue le stock du produit"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity):
        """Augmente le stock du produit"""
        self.stock += quantity
        self.save()


class Order(models.Model):
    """Modèle pour les commandes"""
    
    STATUS_CHOICES = [
        ('pending', 'En préparation'),
        ('paid', 'Payée'),
        ('ready', 'Prête'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Utilisateur",
        null=True,
        blank=True
    )
    customer_name = models.CharField(
        max_length=100, 
        verbose_name="Nom du client"
    )
    customer_email = models.EmailField(
        blank=True, 
        verbose_name="Email du client"
    )
    customer_phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Téléphone du client"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    notes = models.TextField(
        blank=True, 
        verbose_name="Notes"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Prix total (€)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Date de mise à jour"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
    
    def __str__(self):
        return f"Commande #{self.id} - {self.customer_name}"
    
    @property
    def status_label(self):
        """Retourne le label du statut"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    @property
    def items_count(self):
        """Retourne le nombre d'articles dans la commande"""
        return self.items.count()
    
    def calculate_total(self):
        """Calcule le total de la commande"""
        self.total_price = sum(
            item.total_price for item in self.items.all()
        )
        self.save()
        return self.total_price
    
    def cancel_order(self):
        """Annule la commande et restaure le stock"""
        if self.status != 'cancelled':
            # Restaurer le stock des produits
            for item in self.items.all():
                item.product.increase_stock(item.quantity)
            
            self.status = 'cancelled'
            self.save()
    
    def confirm_order(self):
        """Confirme la commande et diminue le stock"""
        if self.status == 'pending':
            # Vérifier et diminuer le stock
            for item in self.items.all():
                if not item.product.decrease_stock(item.quantity):
                    raise ValueError(f"Stock insuffisant pour {item.product.name}")
            
            self.status = 'paid'
            self.save()


class OrderItem(models.Model):
    """Modèle pour les articles d'une commande"""
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Commande"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Produit"
    )
    quantity = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)],
        verbose_name="Quantité"
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Prix unitaire (€)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - Commande #{self.order.id}"
    
    @property
    def total_price(self):
        """Calcule le prix total de l'article"""
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        """Sauvegarde l'article et met à jour le prix unitaire"""
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
        # Mettre à jour le total de la commande
        self.order.calculate_total()


class ContactMessage(models.Model):
    """Modèle pour les messages de contact"""
    
    SUBJECT_CHOICES = [
        ('commande', 'Passer une commande'),
        ('renseignement', 'Demande de renseignement'),
        ('allergene', 'Information sur les allergènes'),
        ('autre', 'Autre'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Utilisateur",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Téléphone"
    )
    subject = models.CharField(
        max_length=20, 
        choices=SUBJECT_CHOICES,
        verbose_name="Sujet"
    )
    message = models.TextField(verbose_name="Message")
    status = models.CharField(
        max_length=20, 
        choices=[
            ('new', 'Nouveau'),
            ('read', 'Lu'),
            ('replied', 'Répondu'),
            ('closed', 'Fermé'),
        ],
        default='new',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
    
    def __str__(self):
        return f"Message de {self.name} - {self.get_subject_display()}"
    
    @property
    def subject_label(self):
        """Retourne le label du sujet"""
        return dict(self.SUBJECT_CHOICES).get(self.subject, self.subject)
