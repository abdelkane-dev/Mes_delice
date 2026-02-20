from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ProductViewSet, OrderViewSet, ContactMessageViewSet

# Créer un routeur pour les API REST
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'contact', ContactMessageViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
