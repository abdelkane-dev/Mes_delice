from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ProductViewSet, OrderViewSet, ContactMessageViewSet, NotificationViewSet, cancel_order_api

# Créer un routeur pour les API REST
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'contact', ContactMessageViewSet, basename='contact')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    # URL d'annulation de commande (avec vérification 1h)
    path('orders/<int:order_id>/cancel/', cancel_order_api, name='cancel_order'),
]
