from PIL import Image, ImageDraw
import os

def create_placeholder_image(filename, color, text):
    img = Image.new('RGB', (300, 200), color)
    draw = ImageDraw.Draw(img)
    draw.text((50, 80), text, fill='white')
    img.save(f'media/products/{filename}')

# Créer quelques images par défaut
os.makedirs('media/products', exist_ok=True)
create_placeholder_image('0a2efc9c7c3df7e154742ec4219c3b16.png', (139, 69, 19), 'Produit 1')
create_placeholder_image('0a2efc9c7c3df7e154742ec4219c3b16_3BOiHU5.png', (19, 139, 69), 'Produit 2')
print("Images par défaut créées")
