# Les Délices de Marie - Système de Gestion de Pâtisserie

Application web Django complète pour la gestion d'une pâtisserie avec interface client et administration.

## 🎯 Fonctionnalités

### Pour les Clients
- ✅ Inscription et authentification
- ✅ Navigation des produits disponibles
- ✅ Passage de commandes personnalisées
- ✅ Suivi de leurs propres commandes
- ✅ Envoi de messages de contact
- ✅ Séparation des données (chaque client voit uniquement ses données)

### Pour les Administrateurs
- ✅ Gestion des produits (CRUD complet)
- ✅ Gestion des stocks avec alertes
- ✅ Gestion des commandes de tous les clients
- ✅ Gestion des messages de contact
- ✅ **NOUVEAU** Gestion des utilisateurs (activation, désactivation, suppression)
- ✅ Visualisation des commandes par utilisateur
- ✅ Statistiques et rapports

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.8+
- Django 4.2+
- SQLite (inclus avec Python)

### Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer les utilisateurs de test
python create_users.py

# Créer des données de test (optionnel)
python create_test_data.py

# Démarrer le serveur
python manage.py runserver 0.0.0.0:8000
```

## 🔐 Comptes de Test

**Administrateur (Superuser):**
- Username: `admin`
- Password: `admin123`
- Accès: Page admin + gestion utilisateurs + Django admin

**Client (Utilisateur normal):**
- Username: `client`
- Password: `client123`
- Accès: Page client uniquement

## 📁 Structure du Projet

```
webapp/
├── api/                          # Application principale
│   ├── models.py                 # Modèles de données (Product, Order, ContactMessage)
│   ├── views.py                  # Vues API REST et Django
│   ├── serializers.py            # Sérialiseurs Django REST Framework
│   ├── urls.py                   # Routes API
│   └── migrations/               # Migrations de base de données
│
├── delices_backend/              # Configuration Django
│   ├── settings.py               # Configuration principale
│   ├── urls.py                   # Routes principales
│   └── wsgi.py                   # Configuration WSGI
│
├── templates/                    # Templates HTML
│   ├── base.html                 # Template de base
│   ├── login.html                # Page de connexion
│   ├── register.html             # Page d'inscription
│   ├── client.html               # Interface client
│   └── admin.html                # Interface admin
│
├── frontend/                     # Fichiers statiques
│   ├── css/                      # Styles CSS
│   ├── js/                       # Scripts JavaScript
│   └── images/                   # Images statiques
│
├── manage.py                     # Script de gestion Django
├── requirements.txt              # Dépendances Python
├── create_users.py               # Script création utilisateurs
└── create_test_data.py           # Script données de test
```

## 🔧 Fonctionnalités Principales

### 1. Gestion des Images
- Images stockées dans `frontend/images/`
- Accès via `{% static 'images/...' %}`
- Support des images produits via URL ou upload

### 2. Séparation des Données par Utilisateur
- **Commandes**: Chaque client voit uniquement ses commandes
- **Messages**: Chaque client voit uniquement ses messages
- **Produits**: Visibles par tous (catalogue commun)
- **Admin**: Voit toutes les données

### 3. Gestion des Utilisateurs (Admin)
- Liste de tous les utilisateurs
- Voir le rôle (Admin / Client)
- Voir le statut (Actif / Inactif)
- Activer / Désactiver un utilisateur
- Supprimer un utilisateur (sauf admins)
- Voir les commandes d'un utilisateur

## 📊 API REST Endpoints

### Produits
```
GET    /api/products/              # Liste des produits
POST   /api/products/              # Créer un produit
GET    /api/products/{id}/         # Détail d'un produit
PUT    /api/products/{id}/         # Modifier un produit
DELETE /api/products/{id}/         # Supprimer un produit
POST   /api/products/{id}/update_stock/  # Mettre à jour le stock
```

### Commandes
```
GET    /api/orders/                # Liste des commandes (filtrées par user)
POST   /api/orders/                # Créer une commande
GET    /api/orders/{id}/           # Détail d'une commande
PUT    /api/orders/{id}/           # Modifier une commande
POST   /api/orders/{id}/update_status/  # Changer le statut
POST   /api/orders/{id}/cancel/    # Annuler une commande
```

### Messages de Contact
```
GET    /api/contact/               # Liste des messages (filtrés par user)
POST   /api/contact/               # Créer un message
GET    /api/contact/{id}/          # Détail d'un message
POST   /api/contact/{id}/mark_as_read/  # Marquer comme lu
```

### Gestion des Utilisateurs (Admin uniquement)
```
GET    /api/users/list/            # Liste tous les utilisateurs
DELETE /api/users/{id}/delete/     # Supprimer un utilisateur
POST   /api/users/{id}/toggle-active/  # Activer/Désactiver
GET    /api/users/{id}/orders/     # Voir les commandes d'un user
```

## 🌐 Routes Web

```
/                      # Page de connexion (accueil)
/register/             # Page d'inscription
/client/               # Interface client
/management/           # Interface admin
/management/users/     # Gestion des utilisateurs
/logout/               # Déconnexion
/admin/                # Django admin (superuser uniquement)
```

## 🔒 Sécurité

- Authentification requise pour toutes les pages sauf login/register
- Séparation stricte admin/client
- Filtrage automatique des données par utilisateur
- Protection CSRF sur toutes les requêtes POST
- Permissions Django REST Framework
- Admin ne peut pas supprimer/modifier d'autres admins

## 🎨 Technologies Utilisées

**Backend:**
- Django 4.2
- Django REST Framework
- SQLite (développement)

**Frontend:**
- HTML5, CSS3
- JavaScript Vanilla
- Font Awesome (icônes)
- Fetch API (requêtes AJAX)

## 📝 Modèles de Données

### Product
- Nom, description, prix, stock
- Catégorie (gâteaux, pâtisseries, etc.)
- Disponibilité, image

### Order
- **User** (ForeignKey) - Utilisateur propriétaire
- Informations client (nom, email, téléphone)
- Statut (pending, paid, ready, delivered, cancelled)
- Prix total, notes

### OrderItem
- Commande, produit, quantité
- Prix unitaire, prix total

### ContactMessage
- **User** (ForeignKey) - Utilisateur propriétaire
- Nom, email, téléphone
- Sujet, message
- Statut (new, read, replied, closed)

## 🚀 Déploiement en Production

1. **Configuration des variables d'environnement**
   ```bash
   # Créer un fichier .env
   SECRET_KEY=votre-clé-secrète
   DEBUG=False
   ALLOWED_HOSTS=votredomaine.com
   ```

2. **Collecte des fichiers statiques**
   ```bash
   python manage.py collectstatic
   ```

3. **Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Créer le superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Démarrer avec Gunicorn**
   ```bash
   gunicorn delices_backend.wsgi:application
   ```

## 📧 Support

Pour toute question ou problème, contactez l'équipe de développement.

## 📄 Licence

Tous droits réservés © Les Délices de Marie

---

**Version**: 2.0
**Dernière mise à jour**: Février 2025
**Statut**: ✅ Production Ready
