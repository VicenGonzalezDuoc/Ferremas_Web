import os
import django
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from django.db import connection

def fix_single_product():
    print("Buscando producto problemático...")
    
    # Obtener todos los productos
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM shop_product")
        products = cursor.fetchall()
    
    print(f"Total de productos encontrados: {len(products)}")
    
    # Verificar cada ID
    for product in products:
        product_id = product[0]
        product_name = product[1]
        
        try:
            # Intentar convertir a UUID
            uuid.UUID(str(product_id))
            print(f"Producto con ID válido: {product_id} - {product_name}")
        except (ValueError, AttributeError):
            print(f"¡PRODUCTO CON ID INVÁLIDO ENCONTRADO!: {product_id} - {product_name}")
            
            # Generar un nuevo UUID válido
            new_uuid = str(uuid.uuid4())
            print(f"Nuevo UUID generado: {new_uuid}")
            
            # Actualizar referencias en CartItem
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_cartitem SET product_id = %s WHERE product_id = %s",
                    [new_uuid, product_id]
                )
                updated_items = cursor.rowcount
                print(f"Actualizados {updated_items} items en el carrito")
            
            # Actualizar el ID del producto
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_product SET id = %s WHERE id = %s",
                    [new_uuid, product_id]
                )
                updated = cursor.rowcount
                if updated:
                    print(f"Producto actualizado exitosamente con nuevo UUID: {new_uuid}")
                else:
                    print("No se pudo actualizar el producto")
            
            # Intentar eliminar el producto si es necesario
            respuesta = input("¿Deseas eliminar este producto? (s/n): ")
            if respuesta.lower() == 's':
                with connection.cursor() as cursor:
                    # Primero eliminar referencias en CartItem
                    cursor.execute(
                        "DELETE FROM shop_cartitem WHERE product_id = %s",
                        [new_uuid]
                    )
                    items_deleted = cursor.rowcount
                    print(f"Eliminados {items_deleted} items del carrito")
                    
                    # Luego eliminar el producto
                    cursor.execute(
                        "DELETE FROM shop_product WHERE id = %s",
                        [new_uuid]
                    )
                    product_deleted = cursor.rowcount
                    if product_deleted:
                        print("Producto eliminado exitosamente")
                    else:
                        print("No se pudo eliminar el producto")

if __name__ == "__main__":
    fix_single_product()