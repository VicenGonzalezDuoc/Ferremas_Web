import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from django.db import connection

def delete_product_3():
    print("Eliminando producto con ID '3'...")
    
    # Eliminar referencias en CartItem
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM shop_cartitem WHERE product_id = '3'")
        cart_items_deleted = cursor.rowcount
        print(f"Eliminados {cart_items_deleted} items del carrito relacionados")
    
    # Eliminar el producto
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM shop_product WHERE id = '3'")
        products_deleted = cursor.rowcount
        print(f"Eliminados {products_deleted} productos con ID '3'")
    
    print("Proceso completado")

if __name__ == "__main__":
    delete_product_3()