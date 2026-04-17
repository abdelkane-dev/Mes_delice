from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Order, ContactMessage
from .serializers import ProductSerializer, OrderSerializer, ContactMessageSerializer

# Vues pour les pages web
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('management')
        else:
            return redirect('client')
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('management')
            else:
                return redirect('client')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Nom utilisateur déjà utilisé'})
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('client')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def client_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_staff:
        return redirect('management')
    return render(request, 'client.html')

def management_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_staff:
        return redirect('client')
    return render(request, 'admin.html')

# API REST Views
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)

class ContactMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        else:
            return ContactMessage.objects.filter(user=self.request.user)

# Vues individuelles pour compatibilité
class ProductList(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderList(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)

class OrderDetail(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)

class ContactMessageList(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        else:
            return ContactMessage.objects.filter(user=self.request.user)

class ContactMessageDetail(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        else:
            return ContactMessage.objects.filter(user=self.request.user)

# Vues pour les notifications
@api_view(['GET'])
def notifications_recent(request):
    """Récupérer les notifications récentes"""
    notifications = []
    return Response(notifications)

@api_view(['GET'])
def notifications_unread_count(request):
    """Compter les notifications non lues"""
    return Response({'count': 0})

# Vues pour les utilisateurs
@api_view(['GET'])
def users_list(request):
    """Lister les utilisateurs"""
    if not request.user.is_staff:
        return Response({'error': 'Accès non autorisé'}, status=403)
    
    from django.contrib.auth.models import User
    users = User.objects.all().values('id', 'username', 'email', 'is_staff', 'is_active')
    return Response(list(users))

# Vues pour les messages de contact avec le bon nom d'endpoint
@api_view(['GET'])
def mes_messages(request):
    """Récupérer les messages de l'utilisateur connecté"""
    messages = ContactMessage.objects.filter(user=request.user)
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)

# Corriger la vue ProductViewSet pour gérer les uploads
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def perform_create(self, serializer):
        # Gérer l'upload d'image
        image = self.request.FILES.get('image')
        if image:
            serializer.save(image=image)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        # Gérer l'upload d'image lors de la mise à jour
        image = self.request.FILES.get('image')
        if image:
            serializer.save(image=image)
        else:
            serializer.save()
