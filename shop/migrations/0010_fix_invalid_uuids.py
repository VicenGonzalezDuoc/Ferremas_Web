from django.db import migrations
import uuid

def fix_invalid_uuids(apps, schema_editor):
    # Obtener el modelo Product desde el estado de la migración
    Product = apps.get_model('shop', 'Product')
    CartItem = apps.get_model('shop', 'CartItem')
    
    # Obtener la conexión a la base de datos
    connection = schema_editor.connection
    
    # Identificar productos con UUIDs inválidos
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM shop_product")
        rows = cursor.fetchall()
    
    for row in rows:
        product_id = row[0]
        try:
            # Verificar si es un UUID válido
            uuid.UUID(str(product_id))
        except (ValueError, AttributeError):
            # Generar un nuevo UUID
            new_id = str(uuid.uuid4())
            
            # Actualizar referencias en CartItem
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_cartitem SET product_id = %s WHERE product_id = %s",
                    [new_id, product_id]
                )
            
            # Actualizar el producto
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_product SET id = %s WHERE id = %s",
                    [new_id, product_id]
                )

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_fix_null_subcategories'),  # Ajusta según tu esquema
    ]

    operations = [
        migrations.RunPython(fix_invalid_uuids),
    ]