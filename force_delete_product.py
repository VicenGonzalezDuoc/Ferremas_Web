import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from django.db import connection

def force_delete_product():
    print("Eliminando producto problemático...")
    
    # Obtener todos los productos
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM shop_product")
        products = cursor.fetchall()
    
    print(f"Total de productos encontrados: {len(products)}")
    
    # Eliminar todos los items del carrito
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM shop_cartitem")
        items_deleted = cursor.rowcount
        print(f"Eliminados {items_deleted} items del carrito")
    
    # Eliminar todos los productos
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM shop_product")
        products_deleted = cursor.rowcount
        print(f"Eliminados {products_deleted} productos")
    
    print("Proceso completado. Todos los productos y items del carrito han sido eliminados.")

if __name__ == "__main__":
    confirmacion = input("¡ADVERTENCIA! Este script eliminará TODOS los productos y items del carrito. ¿Estás seguro? (escribe 'SI' para confirmar): ")
    if confirmacion == "SI":
        force_delete_product()
    else:
        print("Operación cancelada.")