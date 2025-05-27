import os
import django
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from django.db import connection

def fix_product_uuid():
    # ID del producto problemático (ajusta según sea necesario)
    problem_id = '3'  # O el ID que esté causando problemas
    
    print(f"Corrigiendo UUID para el producto con ID: {problem_id}")
    
    # Verificar si el producto existe
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM shop_product WHERE id = %s", [problem_id])
        product = cursor.fetchone()
    
    if not product:
        print(f"No se encontró ningún producto con ID: {problem_id}")
        return
    
    product_name = product[0]
    print(f"Producto encontrado: {product_name}")
    
    # Generar un nuevo UUID válido
    new_uuid = str(uuid.uuid4())
    print(f"Nuevo UUID generado: {new_uuid}")
    
    # Actualizar referencias en CartItem
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE shop_cartitem SET product_id = %s WHERE product_id = %s",
            [new_uuid, problem_id]
        )
        updated_items = cursor.rowcount
        print(f"Actualizados {updated_items} items en el carrito")
    
    # Actualizar el ID del producto
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE shop_product SET id = %s WHERE id = %s",
            [new_uuid, problem_id]
        )
        updated = cursor.rowcount
        if updated:
            print(f"Producto actualizado exitosamente con nuevo UUID: {new_uuid}")
        else:
            print("No se pudo actualizar el producto")

if __name__ == "__main__":
    fix_product_uuid()