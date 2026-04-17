from rest_framework import serializers
from django.core.validators import URLValidator
from .models import Product, Order, OrderItem, ContactMessage

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock', 'available', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_image(self, value):
        # Accepter les URLs et les fichiers
        if not value:
            return None
            
        # Si c'est une URL valide
        if value.startswith(('http://', 'https://')):
            url_validator = URLValidator()
            try:
                url_validator(value)
                return value
            except:
                raise serializers.ValidationError("URL d'image invalide")
        
        # Si c'est un fichier uploadé
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'customer_name', 'customer_email', 'customer_phone', 
                  'items', 'total_amount', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_amount', 'created_at', 'updated_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'user', 'name', 'email', 'phone', 'subject', 'message', 
                  'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
