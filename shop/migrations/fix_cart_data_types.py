from django.db import migrations

def fix_cart_data(apps, schema_editor):
    Cart = apps.get_model('shop', 'Cart')
    # El problema es que estamos intentando usar regex en un ForeignKey
    # Vamos a modificar la consulta para que sea compatible
    
    # Obtener todos los carritos con usuario no nulo
    carts_with_user = Cart.objects.filter(user__isnull=False)
    
    # Iterar sobre ellos y eliminar los que no tienen un ID de usuario válido
    for cart in carts_with_user:
        # Verificar si el ID de usuario no es un número
        try:
            int(cart.user.id)  # Intentar convertir a entero
        except (ValueError, AttributeError):
            # Si no es un número, eliminar el carrito
            cart.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),  # Mantén la dependencia original
    ]

    operations = [
        migrations.RunPython(fix_cart_data),
    ]
