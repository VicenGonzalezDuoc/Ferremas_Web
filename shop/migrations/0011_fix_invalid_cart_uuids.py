from django.db import migrations
import uuid
from django.db import connection

def fix_invalid_cart_uuids(apps, schema_editor):
    """
    Corrige los UUIDs inválidos en los carritos
    """
    # Identificar carritos con UUIDs inválidos
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM shop_cart")
        rows = cursor.fetchall()
    
    for row in rows:
        cart_id = row[0]
        try:
            # Verificar si es un UUID válido
            uuid.UUID(str(cart_id))
        except (ValueError, AttributeError):
            # Generar un nuevo UUID
            new_id = str(uuid.uuid4())
            
            # Actualizar referencias en CartItem
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_cartitem SET cart_id = %s WHERE cart_id = %s",
                    [new_id, cart_id]
                )
            
            # Actualizar el carrito
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_cart SET id = %s WHERE id = %s",
                    [new_id, cart_id]
                )

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_fix_invalid_uuids'),  # Ajusta según tu esquema
    ]

    operations = [
        migrations.RunPython(fix_invalid_cart_uuids),
    ]