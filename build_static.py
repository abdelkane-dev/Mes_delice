#!/usr/bin/env python
"""
Script de build pour les fichiers statiques - version robuste pour Render
"""
import os
import shutil
from pathlib import Path

def build_static():
    """Copie les fichiers statiques vers staticfiles"""
    
    print("🔨 Construction des fichiers statiques...")
    
    # Chemins
    base_dir = Path(__file__).resolve().parent
    frontend_dir = base_dir / 'frontend'
    staticfiles_dir = base_dir / 'staticfiles'
    
    # Supprimer l'ancien staticfiles
    if staticfiles_dir.exists():
        print(f"🗑️  Suppression de {staticfiles_dir}")
        shutil.rmtree(staticfiles_dir)
    
    # Créer le répertoire staticfiles
    staticfiles_dir.mkdir(exist_ok=True)
    
    # Copier les fichiers
    print(f"📁 Copie depuis {frontend_dir} vers {staticfiles_dir}")
    
    # Copier CSS
    css_src = frontend_dir / 'css'
    css_dst = staticfiles_dir / 'css'
    if css_src.exists():
        css_dst.mkdir(exist_ok=True)
        for file in css_src.glob('*.css'):
            print(f"   📄 Copie de {file.name}")
            shutil.copy2(file, css_dst)
    
    # Copier JS
    js_src = frontend_dir / 'js'
    js_dst = staticfiles_dir / 'js'
    if js_src.exists():
        js_dst.mkdir(exist_ok=True)
        for file in js_src.glob('*.js'):
            print(f"   📄 Copie de {file.name}")
            shutil.copy2(file, js_dst)
    
    # Copier images
    img_src = frontend_dir / 'images'
    img_dst = staticfiles_dir / 'images'
    if img_src.exists():
        img_dst.mkdir(exist_ok=True)
        for file in img_src.glob('*'):
            print(f"   🖼️  Copie de {file.name}")
            shutil.copy2(file, img_dst)
    
    # Copier favicon
    favicon_src = frontend_dir / 'favicon.svg'
    if favicon_src.exists():
        print(f"   🎨 Copie de favicon.svg")
        shutil.copy2(favicon_src, staticfiles_dir / 'favicon.svg')
    
    print("✅ Fichiers statiques construits avec succès!")
    
    # Vérifier
    css_files = list((staticfiles_dir / 'css').glob('*.css'))
    js_files = list((staticfiles_dir / 'js').glob('*.js'))
    
    print(f"📊 Résultat: {len(css_files)} fichiers CSS, {len(js_files)} fichiers JS")

if __name__ == "__main__":
    build_static()
