from django.core.management.base import BaseCommand
from django.db import connection
from shop.models import Cart, CartItem
import uuid
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Limpia carritos antiguos y con datos inválidos'

    def handle(self, *args, **options):
        self.stdout.write('Limpiando carritos...')
        
        # 1. Eliminar carritos antiguos (más de 30 días)
        old_date = timezone.now() - timedelta(days=30)
        old_carts = Cart.objects.filter(updated_at__lt=old_date)
        count = old_carts.count()
        old_carts.delete()
        self.stdout.write(f'Eliminados {count} carritos antiguos')
        
        # 2. Limpiar carritos con UUIDs inválidos
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM shop_cart")
            rows = cursor.fetchall()
        
        invalid_carts = []
        for row in rows:
            cart_id = row[0]
            try:
                uuid.UUID(str(cart_id))
            except (ValueError, AttributeError):
                invalid_carts.append(cart_id)
        
        if invalid_carts:
            self.stdout.write(f'Encontrados {len(invalid_carts)} carritos con UUIDs inválidos')
            for cart_id in invalid_carts:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM shop_cartitem WHERE cart_id = %s", [cart_id])
                    cursor.execute("DELETE FROM shop_cart WHERE id = %s", [cart_id])
            
            self.stdout.write(f'Eliminados {len(invalid_carts)} carritos inválidos')
        
        self.stdout.write('Limpieza completada con éxito')