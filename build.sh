#!/bin/bash
# Script de build pour Render

echo "Ì¥® Installation des d√©pendances..."
pip install -r requirements.txt

echo "Ì¥ç Diagnostic de la configuration..."
python debug_render.py

echo "Ì∑ÑÔ∏è Migration de la base de donn√©es..."
python manage.py migrate

echo "Ì¥ß Cr√©ation superuser si n√©cessaire..."
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
    print("‚úÖ Superuser cr√©√©")
else:
    print("‚úÖ Superuser existe d√©j√†")
