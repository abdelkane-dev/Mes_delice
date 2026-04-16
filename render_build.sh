#!/bin/bash
# Script de build pour Render
set -e  # Arrêter en cas d'erreur

echo "🔨 Installation des dépendances..."
pip install -r requirements.txt

echo "🔍 Diagnostic de la configuration..."
python debug_render.py

echo "🗄️  Migration de la base de données..."
python manage.py migrate --noinput || echo "⚠️ Migration échouée, continuation..."

echo "🔧 Création superuser si nécessaire..."
python manage.py shell -c "
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@delices.com', 'admin123')
        print('✅ Superuser admin créé')
    else:
        print('✅ Superuser admin existe déjà')
except Exception as e:
    print(f'⚠️ Erreur création superuser: {e}')
" || echo "⚠️ Création superuser échouée"

echo "📁 Création des répertoires statiques et media..."
mkdir -p staticfiles/css
mkdir -p staticfiles/js
mkdir -p staticfiles/images
mkdir -p media  # Créer le répertoire media pour les uploads

echo "📄 Copie des fichiers statiques..."
cp -r frontend/css/* staticfiles/css/ 2>/dev/null || echo "⚠️ CSS déjà copié"
cp -r frontend/js/* staticfiles/js/ 2>/dev/null || echo "⚠️ JS déjà copié"
cp -r frontend/images/* staticfiles/images/ 2>/dev/null || echo "⚠️ Images déjà copiées"
cp frontend/favicon.svg staticfiles/ 2>/dev/null || echo "⚠️ Favicon déjà copié"

echo "🗑️  Nettoyage ancien collectstatic..."
rm -rf staticfiles/static/

echo "📈 Collectstatic..."
python manage.py collectstatic --noinput || echo "⚠️ Collectstatic échoué"

echo "✅ Build terminé!"
echo "📊 Contenu de staticfiles:"
ls -la staticfiles/ || echo "⚠️ staticfiles vide"
echo "📁 Contenu de media:"
ls -la media/ || echo "⚠️ media vide"
