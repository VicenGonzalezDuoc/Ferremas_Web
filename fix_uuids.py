import os
import django
import uuid
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferremas.settings')
django.setup()

from shop.models import Product
from django.db import connection

def fix_invalid_uuids():
    print("Iniciando corrección de UUIDs inválidos...")
    
    # Obtener todos los IDs directamente de la base de datos
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM shop_product")
        rows = cursor.fetchall()
    
    total_products = len(rows)
    invalid_count = 0
    fixed_count = 0
    
    print(f"Encontrados {total_products} productos en total")
    
    # Verificar cada ID
    for row in rows:
        product_id = row[0]
        try:
            # Intentar convertir a UUID
            uuid.UUID(str(product_id))
        except (ValueError, AttributeError):
            invalid_count += 1
            print(f"ID inválido encontrado: {product_id}")
            
            # Obtener el producto directamente de la base de datos
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT code, name, description, price, stock, subcategory_id, image, image_url FROM shop_product WHERE id = %s",
                    [product_id]
                )
                product_data = cursor.fetchone()
            
            if product_data:
                # Generar un nuevo UUID
                new_id = uuid.uuid4()
                
                # Actualizar el producto con el nuevo UUID
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE shop_product 
                        SET id = %s 
                        WHERE id = %s
                        """,
                        [str(new_id), product_id]
                    )
                
                fixed_count += 1
                print(f"  - Corregido: {product_id} -> {new_id}")
    
    print(f"\nResumen:")
    print(f"- Total de productos: {total_products}")
    print(f"- UUIDs inválidos encontrados: {invalid_count}")
    print(f"- UUIDs corregidos: {fixed_count}")
    
    if invalid_count == 0:
        print("\n¡No se encontraron UUIDs inválidos!")
    elif fixed_count == invalid_count:
        print("\n¡Todos los UUIDs inválidos han sido corregidos!")
    else:
        print(f"\nATENCIÓN: No se pudieron corregir todos los UUIDs inválidos ({invalid_count - fixed_count} restantes)")

if __name__ == "__main__":
    fix_invalid_uuids()