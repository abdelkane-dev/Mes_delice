from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('gateaux', 'Gâteaux'),
        ('patisseries', 'Pâtisseries'),
        ('viennoiseries', 'Viennoiseries'),
        ('confiseries', 'Confiseries'),
        ('boissons', 'Boissons'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Catégorie")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    available = models.BooleanField(default=True, verbose_name="Disponible")
    image = models.URLField(max_length=500, blank=True, null=True, verbose_name="Image URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('ready', 'Prêt'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    customer_name = models.CharField(max_length=200, verbose_name="Nom du client")
    customer_email = models.EmailField(verbose_name="Email du client")
    customer_phone = models.CharField(max_length=20, verbose_name="Téléphone du client")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commande #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Commande")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total")
    
    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('closed', 'Fermé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    name = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message de {self.name} - {self.subject}"
