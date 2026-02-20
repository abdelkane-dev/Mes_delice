#!/bin/bash
# Script de build pour Render
echo "🔨 Installation des dépendances..."
pip install -r requirements.txt

echo "📁 Création des répertoires statiques..."
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
