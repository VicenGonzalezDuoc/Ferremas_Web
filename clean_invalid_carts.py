import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from django.db import connection
import uuid

def clean_invalid_carts():
    print("Limpiando carritos con UUIDs inválidos...")
    
    # 1. Identificar carritos con UUIDs inválidos
    invalid_carts = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM shop_cart")
        rows = cursor.fetchall()
    
    for row in rows:
        cart_id = row[0]
        try:
            uuid.UUID(str(cart_id))
        except (ValueError, AttributeError):
            invalid_carts.append(cart_id)
    
    if invalid_carts:
        print(f"Encontrados {len(invalid_carts)} carritos con UUIDs inválidos: {invalid_carts}")
        
        # 2. Eliminar items del carrito que referencian a estos carritos
        for cart_id in invalid_carts:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_cartitem WHERE cart_id = %s",
                    [cart_id]
                )
                deleted_count = cursor.rowcount
                print(f"Eliminados {deleted_count} items del carrito para el carrito {cart_id}")
        
        # 3. Eliminar los carritos inválidos
        for cart_id in invalid_carts:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_cart WHERE id = %s",
                    [cart_id]
                )
                deleted_count = cursor.rowcount
                print(f"Eliminado carrito {cart_id}")
        
        print("Limpieza de carritos completada.")
    else:
        print("No se encontraron carritos con UUIDs inválidos.")

if __name__ == "__main__":
    clean_invalid_carts()