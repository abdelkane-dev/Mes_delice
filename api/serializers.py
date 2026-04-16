from rest_framework import serializers
from .models import Product, Order, OrderItem, ContactMessage, Notification
from django.utils.text import slugify


class ProductSerializer(serializers.ModelSerializer):
    """Serializer pour les produits"""
    
    stock_status = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, use_url=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock', 
            'available', 'category', 'category_display', 'image', 
            'stock_status', 'is_in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_price(self, value):
        """Valide que le prix est positif"""
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0")
        return value
    
    def validate_stock(self, value):
        """Valide que le stock est non négatif"""
        if value < 0:
            raise serializers.ValidationError("Le stock ne peut pas être négatif")
        return value
    
    def validate_image(self, value):
        """Validate image field: accept None or an uploaded file; keep existing behavior for strings."""
        if value in (None, ''):
            return None
        # If value is a string (existing data), allow it through
        if isinstance(value, str):
            return value
        return value
    
    def create(self, validated_data):
        """Crée un produit avec un slug automatique"""
        name = validated_data.get('name', '')
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(name)
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer pour les articles de commande"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_details = ProductSerializer(source='product', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name', 'product_details',
            'quantity', 'unit_price', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'unit_price', 'created_at']
    
    def validate_quantity(self, value):
        """Valide que la quantité est positive"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.ReadOnlyField()
    can_cancel = serializers.SerializerMethodField()
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone', 
            'notes', 'status', 'status_display', 
            'total_price', 'refund_amount', 'items_count', 'can_cancel',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_can_cancel(self, obj):
        """Retourne si la commande peut être annulée, le message et le temps restant"""
        from django.utils import timezone
        can_cancel, message = obj.can_cancel()
        # Calculer le temps restant avant de pouvoir annuler (en secondes)
        time_diff = timezone.now() - obj.created_at
        seconds_passed = time_diff.total_seconds()
        wait_seconds = 3600  # 1 heure
        seconds_remaining = max(0, wait_seconds - seconds_passed)
        return {
            'can_cancel': can_cancel,
            'message': message,
            'seconds_remaining': int(seconds_remaining)
        }
    
    def validate_customer_name(self, value):
        """Valide que le nom du client n'est pas vide"""
        if not value.strip():
            raise serializers.ValidationError("Le nom du client est requis")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une commande avec ses articles"""
    
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'notes', 'items'
        ]
    
    def validate_items(self, value):
        """Valide que les articles de la commande sont corrects"""
        if not value:
            raise serializers.ValidationError("La commande doit contenir au moins un article")
        
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Chaque article doit contenir 'product_id' et 'quantity'"
                )
            
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Le produit avec l'ID {item['product_id']} n'existe pas"
                )
            
            if not product.available:
                raise serializers.ValidationError(
                    f"Le produit '{product.name}' n'est pas disponible"
                )
            
            quantity = item['quantity']
            if quantity <= 0:
                raise serializers.ValidationError("La quantité doit être supérieure à 0")
            
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Stock insuffisant pour '{product.name}'. Disponible: {product.stock}"
                )
        
        return value
    
    def create(self, validated_data):
        """Crée la commande et ses articles"""
        items_data = validated_data.pop('items')
        
        # Créer la commande
        order = Order.objects.create(**validated_data)
        
        # Créer les articles de la commande
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price
            )
            
            # Diminuer le stock
            product.decrease_stock(item_data['quantity'])
        
        # Calculer le total
        order.calculate_total()
        
        return order


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages de contact"""
    
    subject_label = serializers.ReadOnlyField()
    est_repondu = serializers.ReadOnlyField()
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'subject_label',
            'message', 'status', 'created_at',
            'admin_reponse', 'repondu_le', 'est_repondu'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'admin_reponse', 'repondu_le', 'est_repondu']
    
    def validate_message(self, value):
        """Valide que le message n'est pas vide"""
        if not value.strip():
            raise serializers.ValidationError("Le message ne peut pas être vide")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications"""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'type_display', 'message', 'lien',
            'est_lue', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
