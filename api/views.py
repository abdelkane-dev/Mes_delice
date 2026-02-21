from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, Order, OrderItem, ContactMessage
from .serializers import (
    ProductSerializer, 
    OrderSerializer, 
    OrderCreateSerializer,
    OrderItemSerializer,
    ContactMessageSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les produits
    
    Liste, crée, récupère, met à jour et supprime les produits
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Filtre les produits par catégorie et disponibilité"""
        queryset = Product.objects.all()
        
        # Filtre par catégorie
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtre par disponibilité
        available = self.request.query_params.get('available', None)
        if available is not None:
            is_available = available.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(available=is_available)
        
        # Filtre par stock
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None:
            is_in_stock = in_stock.lower() in ['true', '1', 'yes']
            if is_in_stock:
                queryset = queryset.filter(stock__gt=0, available=True)
            else:
                queryset = queryset.filter(Q(stock=0) | Q(available=False))
        
        # Recherche par nom
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """
        Met à jour le stock d'un produit
        
        Body: { "stock": 50 }
        """
        product = self.get_object()
        new_stock = request.data.get('stock')
        
        if new_stock is None:
            return Response(
                {'error': 'Le champ "stock" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Le stock doit être un nombre entier positif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.stock = new_stock
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """
        Active/désactive la disponibilité d'un produit
        """
        product = self.get_object()
        product.available = not product.available
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Retourne les produits avec un stock faible (≤ 5)
        """
        products = Product.objects.filter(stock__lte=5, stock__gt=0, available=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """
        Retourne les produits en rupture de stock
        """
        products = Product.objects.filter(stock=0, available=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commandes
    
    Liste, crée, récupère, met à jour et supprime les commandes
    """
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        """Utilise des serializers différents selon l'action"""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Filtre les commandes par statut et par utilisateur"""
        queryset = Order.objects.all().prefetch_related('items__product')
        
        # Les clients ne voient que leurs propres commandes
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        
        # Filtre par statut
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filtre par client
        customer = self.request.query_params.get('customer', None)
        if customer:
            queryset = queryset.filter(
                Q(customer_name__icontains=customer) | 
                Q(customer_email__icontains=customer)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crée une nouvelle commande"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Associer la commande à l'utilisateur connecté
        order = serializer.save(user=request.user if request.user.is_authenticated else None)
        
        # Retourner la commande complète avec les articles
        response_serializer = OrderSerializer(order)
        return Response(
            response_serializer.data, 
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Met à jour le statut d'une commande
        
        Body: { "status": "paid" }
        Statuts possibles: pending, paid, ready, delivered, cancelled
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Le champ "status" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {
                    'error': f'Statut invalide. Valeurs autorisées: {", ".join(valid_statuses)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Annule une commande et restaure le stock
        """
        order = self.get_object()
        
        if order.status == 'cancelled':
            return Response(
                {'error': 'Cette commande est déjà annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if order.status == 'delivered':
            return Response(
                {'error': 'Impossible d\'annuler une commande déjà livrée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.cancel_order()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirme une commande (passe en statut 'paid')
        """
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'error': 'Seules les commandes en attente peuvent être confirmées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order.confirm_order()
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Retourne des statistiques sur les commandes
        """
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        paid_orders = Order.objects.filter(status='paid').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        
        total_revenue = sum(
            order.total_price 
            for order in Order.objects.filter(status__in=['paid', 'ready', 'delivered'])
        )
        
        return Response({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'paid_orders': paid_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': float(total_revenue)
        })


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les messages de contact
    
    Liste, crée, récupère, met à jour et supprime les messages
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    
    def get_queryset(self):
        """Filtre les messages par statut et par utilisateur"""
        queryset = ContactMessage.objects.all()
        
        # Les clients ne voient que leurs propres messages
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        
        # Filtre par statut
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filtre par sujet
        subject = self.request.query_params.get('subject', None)
        if subject:
            queryset = queryset.filter(subject=subject)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marque un message comme lu
        """
        message = self.get_object()
        message.status = 'read'
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_replied(self, request, pk=None):
        """
        Marque un message comme répondu
        """
        message = self.get_object()
        message.status = 'replied'
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Crée un nouveau message"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Associer le message à l'utilisateur connecté
        message = serializer.save(user=request.user if request.user.is_authenticated else None)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Retourne les messages non lus
        """
        messages = ContactMessage.objects.filter(status='new')
        # Filtrer par utilisateur si pas admin
        if not request.user.is_superuser:
            messages = messages.filter(user=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


# ============================================
# API pour la gestion des utilisateurs (admin uniquement)
# ============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import JsonResponse

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user_api(request, user_id):
    """Supprime un utilisateur (admin uniquement)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Empêcher la suppression de soi-même
        if user == request.user:
            return JsonResponse({'error': 'Vous ne pouvez pas supprimer votre propre compte'}, status=400)
        
        # Empêcher la suppression d'autres superusers
        if user.is_superuser:
            return JsonResponse({'error': 'Impossible de supprimer un administrateur'}, status=403)
        
        username = user.username
        user.delete()
        
        return JsonResponse({'success': True, 'message': f'Utilisateur {username} supprimé avec succès'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggle_user_active_api(request, user_id):
    """Active/désactive un utilisateur (admin uniquement)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Empêcher la modification de soi-même
        if user == request.user:
            return JsonResponse({'error': 'Vous ne pouvez pas modifier votre propre statut'}, status=400)
        
        # Empêcher la modification d'autres superusers
        if user.is_superuser:
            return JsonResponse({'error': 'Impossible de modifier un administrateur'}, status=403)
        
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'activé' if user.is_active else 'désactivé'
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {user.username} {status_text}',
            'is_active': user.is_active
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_orders_api(request, user_id):
    """Récupère les commandes d'un utilisateur (admin uniquement)"""
    try:
        user = User.objects.get(id=user_id)
        orders = Order.objects.filter(user=user).prefetch_related('items__product')
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'customer_name': order.customer_name,
                'customer_email': order.customer_email,
                'status': order.status,
                'status_label': order.status_label,
                'total_price': float(order.total_price),
                'items_count': order.items_count,
                'created_at': order.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'orders': orders_data,
            'total_orders': len(orders_data)
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_users_api(request):
    """Liste tous les utilisateurs (admin uniquement)"""
    try:
        users = User.objects.all().order_by('-date_joined')
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'orders_count': user.orders.count() if hasattr(user, 'orders') else 0,
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'total_users': len(users_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================
# Vues Django pour les templates
# ============================================

def login_view(request):
    """
    Vue de connexion principale (page d'accueil)
    - Si déjà connecté : redirige vers la bonne page selon le rôle
    - Si superuser : vers admin
    - Si utilisateur normal : vers client
    """
    if request.user.is_authenticated:
        # Redirection selon le rôle
        if request.user.is_superuser:
            return redirect('admin_view')
        else:
            return redirect('client_view')
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            print(f"DEBUG: Tentative connexion - username: {username}")
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.username}!')
                
                # Redirection selon le rôle
                if user.is_superuser:
                    return redirect('admin_view')
                else:
                    return redirect('client_view')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
                print(f"DEBUG: Échec connexion pour {username}")
                
        except Exception as e:
            print(f"ERROR: Erreur connexion: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur technique: {str(e)}')
    
    return render(request, 'login.html')


def register_view(request):
    """
    Vue d'inscription pour les clients uniquement
    """
    if request.user.is_authenticated:
        return redirect('client_view')
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            print(f"DEBUG: Tentative inscription - username: {username}, email: {email}")
            
            # Validation
            if not username or not email or not password:
                messages.error(request, 'Tous les champs sont obligatoires.')
            elif password != password_confirm:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Cet email est déjà utilisé.')
            else:
                # Créer le compte client (pas de superuser)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, f'Compte créé pour {username}! Vous pouvez maintenant vous connecter.')
                print(f"DEBUG: Compte créé avec succès - {username}")
                return redirect('login')
                
        except Exception as e:
            print(f"ERROR: Erreur inscription: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erreur technique: {str(e)}')
    
    return render(request, 'register.html')


@login_required(login_url='login')
def client_view(request):
    """
    Vue principale pour les clients (utilisateurs normaux)
    Accessible uniquement aux utilisateurs connectés NON superuser
    """
    # Si c'est un superuser, rediriger vers admin
    if request.user.is_superuser:
        return redirect('admin_view')
    
    return render(request, 'client.html')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_view(request):
    """
    Vue d'administration
    Accessible uniquement aux superusers
    """
    return render(request, 'admin.html')


def logout_view(request):
    """
    Vue de déconnexion
    Déconnecte l'utilisateur et redirige vers login
    """
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def users_management_view(request):
    """
    Vue de gestion des utilisateurs (admin uniquement)
    Accessible uniquement aux superusers
    """
    # Récupérer tous les utilisateurs sauf le superuser actuel
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'inactive_users': users.filter(is_active=False).count(),
    }
    
    return render(request, 'users_management.html', context)
