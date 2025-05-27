import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from django.db import connection
from shop.models import Cart, CartItem
import uuid

def clean_cart():
    print("Limpiando carritos con productos inválidos...")
    
    # 1. Identificar productos con UUIDs inválidos
    invalid_products = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM shop_product")
        rows = cursor.fetchall()
    
    for row in rows:
        product_id = row[0]
        try:
            uuid.UUID(str(product_id))
        except (ValueError, AttributeError):
            invalid_products.append(product_id)
    
    if invalid_products:
        print(f"Encontrados {len(invalid_products)} productos con UUIDs inválidos: {invalid_products}")
        
        # 2. Eliminar items del carrito que referencian a estos productos
        for product_id in invalid_products:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_cartitem WHERE product_id = %s",
                    [product_id]
                )
                deleted_count = cursor.rowcount
                print(f"Eliminados {deleted_count} items del carrito para el producto {product_id}")
        
        print("Limpieza de carritos completada.")
    else:
        print("No se encontraron productos con UUIDs inválidos.")

if __name__ == "__main__":
    clean_cart()