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
    path('api/products/', views.ProductList.as_view(), name='product-list'),
    path('api/products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('api/orders/', views.OrderList.as_view(), name='order-list'),
    path('api/orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('api/contact/', views.ContactMessageList.as_view(), name='contact-list'),
    path('api/contact/<int:pk>/', views.ContactMessageDetail.as_view(), name='contact-detail'),
]
