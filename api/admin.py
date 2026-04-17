from django.contrib import admin
from .models import Product, Order, OrderItem, ContactMessage, Notification
 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available', 'created_at')
    list_filter = ('category', 'available', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
 
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('product', 'order')
    search_fields = ('product__name', 'order__customer_name')
    ordering = ('-order__created_at',)
 
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
 
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'message', 'est_lue', 'created_at')
    list_filter = ('type', 'est_lue', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
