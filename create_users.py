#!/usr/bin/env python3
"""
Script pour créer les utilisateurs de test
Usage: python create_users.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delices_backend.settings')
django.setup()

from django.contrib.auth.models import User

def create_users():
    """Crée un superuser admin et un utilisateur client normal"""
    
    # Créer le superuser (ADMIN)
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@delices.fr',
            password='admin123'
        )
        print('✅ Superuser créé:')
        print('   Username: admin')
        print('   Password: admin123')
        print('   → Accès à la page ADMIN')
    else:
        print('ℹ️  Superuser "admin" existe déjà')
    
    # Créer un utilisateur normal (CLIENT)
    if not User.objects.filter(username='client').exists():
        client = User.objects.create_user(
            username='client',
            email='client@delices.fr',
            password='client123'
        )
        print('\n✅ Utilisateur client créé:')
        print('   Username: client')
        print('   Password: client123')
        print('   → Accès à la page CLIENT')
    else:
        print('\nℹ️  Utilisateur "client" existe déjà')
    
    print('\n' + '='*50)
    print('RÉCAPITULATIF:')
    print('='*50)
    print('🔐 ADMIN (Superuser):')
    print('   • Username: admin')
    print('   • Password: admin123')
    print('   • Accès: Page ADMIN + Django Admin')
    print()
    print('👤 CLIENT (Utilisateur normal):')
    print('   • Username: client')
    print('   • Password: client123')
    print('   • Accès: Page CLIENT uniquement')
    print('='*50)

if __name__ == '__main__':
    create_users()
