from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.templatetags.static import static as static_file
from api.views import (
    client_view,
    login_view,
    admin_view,
    logout_view,
    register_view,
    users_management_view,
    delete_user_api,
    toggle_user_active_api,
    get_user_orders_api,
    list_users_api,
)

urlpatterns = [
    # Serve favicon from static files
    path('favicon.ico', RedirectView.as_view(url=static_file('favicon.svg'), permanent=False)),
    
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API REST
    path('api/', include('api.urls')),
    
    # API Gestion des utilisateurs (admin uniquement)
    path('api/users/list/', list_users_api, name='list_users_api'),
    path('api/users/<int:user_id>/delete/', delete_user_api, name='delete_user_api'),
    path('api/users/<int:user_id>/toggle-active/', toggle_user_active_api, name='toggle_user_active_api'),
    path('api/users/<int:user_id>/orders/', get_user_orders_api, name='get_user_orders_api'),
    
    # Page principale - sert le frontend SPA
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Routes legacy pour compatibilité (redirigent vers le SPA)
    path('client/', TemplateView.as_view(template_name='index.html'), name='client_view'),
    path('management/', TemplateView.as_view(template_name='index.html'), name='admin_view'),
    path('management/users/', TemplateView.as_view(template_name='index.html'), name='users_management'),
    path('register/', TemplateView.as_view(template_name='index.html'), name='register'),
    path('logout/', TemplateView.as_view(template_name='index.html'), name='logout'),
]

# Servir les fichiers media et static en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration de l'admin
admin.site.site_header = "Les Délices de Marie - Administration"
admin.site.site_title = "Administration Délices de Marie"
admin.site.index_title = "Gestion de la pâtisserie"
