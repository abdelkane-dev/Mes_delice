from django.urls import path
from . import views

urlpatterns = [
    # Pages web
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('client/', views.client_view, name='client'),
    path('management/', views.management_view, name='management'),
    
    # API REST
    path('api/products/', views.ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('api/products/<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='product-detail'),
    path('api/orders/', views.OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('api/orders/<int:pk>/', views.OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='order-detail'),
    path('api/contact/', views.ContactMessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='contact-list'),
    path('api/contact/<int:pk>/', views.ContactMessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='contact-detail'),
    
    # Notifications
    path('api/notifications/recent/', views.notifications_recent, name='notifications-recent'),
    path('api/notifications/unread_count/', views.notifications_unread_count, name='notifications-unread-count'),
]
