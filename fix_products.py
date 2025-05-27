import os
import django
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from shop.models import Product, CartItem
from django.db import connection, transaction

def fix_products():
    print("Iniciando corrección de productos con UUIDs inválidos...")
    
    # Obtener todos los IDs directamente de la base de datos
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM shop_product")
        rows = cursor.fetchall()
    
    total_products = len(rows)
    invalid_count = 0
    fixed_count = 0
    
    print(f"Encontrados {total_products} productos en total")
    
    for row in rows:
        product_id = row[0]
        try:
            # Verificar si es un UUID válido
            uuid.UUID(str(product_id))
        except (ValueError, AttributeError):
            invalid_count += 1
            print(f"ID inválido encontrado: {product_id}")
            
            # Obtener datos del producto
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT code, name, description, price, stock, subcategory_id, image, image_url 
                    FROM shop_product 
                    WHERE id = %s
                    """,
                    [product_id]
                )
                product_data = cursor.fetchone()
            
            if product_data:
                code, name, description, price, stock, subcategory_id, image, image_url = product_data
                
                # Eliminar referencias en CartItem
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM shop_cartitem WHERE product_id = %s",
                        [product_id]
                    )
                
                # Eliminar el producto con UUID inválido
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM shop_product WHERE id = %s",
                        [product_id]
                    )
                
                # Crear un nuevo producto con UUID válido
                new_id = uuid.uuid4()
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO shop_product 
                        (id, code, name, description, price, stock, subcategory_id, image, image_url) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [str(new_id), code, name, description, price, stock, subcategory_id, image, image_url]
                    )
                
                fixed_count += 1
                print(f"  - Producto recreado: {product_id} -> {new_id}")
    
    print("\nResumen:")
    print(f"- Total de productos: {total_products}")
    print(f"- UUIDs inválidos encontrados: {invalid_count}")
    print(f"- Productos recreados: {fixed_count}")

if __name__ == "__main__":
    fix_products()