#!/bin/bash
# Script de build pour Render
echo "🔨 Installation des dépendances..."
pip install -r requirements.txt

echo "🔍 Diagnostic de la configuration..."
python debug_render.py

echo "🗄️  Migration de la base de données..."
python manage.py migrate --noinput

echo "� Création superuser si nécessaire..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@delices.com', 'admin123')
    print('✅ Superuser admin créé')
else:
    print('✅ Superuser admin existe déjà')
"

echo "�📁 Création des répertoires statiques..."
mkdir -p staticfiles/css
mkdir -p staticfiles/js
mkdir -p staticfiles/images

echo "📄 Copie des fichiers statiques..."
cp -r frontend/css/* staticfiles/css/ 2>/dev/null || echo "CSS déjà copié"
cp -r frontend/js/* staticfiles/js/ 2>/dev/null || echo "JS déjà copié"
cp -r frontend/images/* staticfiles/images/ 2>/dev/null || echo "Images déjà copiées"
cp frontend/favicon.svg staticfiles/ 2>/dev/null || echo "Favicon déjà copié"

echo "🗑️  Nettoyage ancien collectstatic..."
rm -rf staticfiles/static/

echo "✅ Build terminé!"
ls -la staticfiles/
