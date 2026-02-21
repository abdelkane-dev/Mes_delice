from django.contrib import admin
from .models import Product, Order, OrderItem, ContactMessage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Interface d'administration pour les produits"""
    
    list_display = ['name', 'category', 'price', 'stock', 'available', 'stock_status', 'created_at']
    list_filter = ['category', 'available', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'available']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'description', 'category', 'image')
        }),
        ('Prix et stock', {
            'fields': ('price', 'stock', 'available')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'stock_status']
    
    def stock_status(self, obj):
        """Affiche le statut du stock avec des couleurs"""
        status = obj.stock_status
        colors = {
            'en stock': 'green',
            'stock faible': 'orange',
            'rupture': 'red',
            'non disponible': 'gray'
        }
        color = colors.get(status, 'black')
        return f'<span style="color: {color}; font-weight: bold;">{status}</span>'
    
    stock_status.allow_tags = True
    stock_status.short_description = 'Statut du stock'


class OrderItemInline(admin.TabularInline):
    """Inline pour les articles d'une commande"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'unit_price', 'total_price']
    
    def total_price(self, obj):
        """Affiche le prix total de l'article"""
        if obj.id:
            return f"{obj.total_price:.2f} FCFA"
        return "-"
    
    total_price.short_description = 'Prix total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Interface d'administration pour les commandes"""
    
    list_display = ['id', 'customer_name', 'status', 'total_price', 'items_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'customer_phone']
    list_editable = ['status']
    ordering = ['-created_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations client', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Commande', {
            'fields': ('status', 'notes', 'total_price')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    
    actions = ['mark_as_paid', 'mark_as_delivered', 'cancel_orders']
    
    def mark_as_paid(self, request, queryset):
        """Marque les commandes comme payées"""
        updated = queryset.filter(status='pending').update(status='paid')
        self.message_user(request, f'{updated} commande(s) marquée(s) comme payée(s)')
    
    mark_as_paid.short_description = "Marquer comme payée"
    
    def mark_as_delivered(self, request, queryset):
        """Marque les commandes comme livrées"""
        updated = queryset.filter(status__in=['paid', 'ready']).update(status='delivered')
        self.message_user(request, f'{updated} commande(s) marquée(s) comme livrée(s)')
    
    mark_as_delivered.short_description = "Marquer comme livrée"
    
    def cancel_orders(self, request, queryset):
        """Annule les commandes sélectionnées"""
        count = 0
        for order in queryset:
            if order.status not in ['cancelled', 'delivered']:
                order.cancel_order()
                count += 1
        self.message_user(request, f'{count} commande(s) annulée(s)')
    
    cancel_orders.short_description = "Annuler les commandes"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Interface d'administration pour les articles de commande"""
    
    list_display = ['id', 'order', 'product', 'quantity', 'unit_price', 'total_price_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__customer_name', 'product__name']
    ordering = ['-created_at']
    
    readonly_fields = ['total_price']
    
    def total_price_display(self, obj):
        """Affiche le prix total"""
        return f"{obj.total_price:.2f} FCFA"
    
    total_price_display.short_description = 'Prix total'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Interface d'administration pour les messages de contact"""
    
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['status']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations contact', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message', 'status')
        }),
        ('Date', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        """Marque les messages comme lus"""
        updated = queryset.filter(status='new').update(status='read')
        self.message_user(request, f'{updated} message(s) marqué(s) comme lu(s)')
    
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_replied(self, request, queryset):
        """Marque les messages comme répondus"""
        updated = queryset.update(status='replied')
        self.message_user(request, f'{updated} message(s) marqué(s) comme répondu(s)')
    
    mark_as_replied.short_description = "Marquer comme répondu"
