from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Product, PriceHistory

@receiver(pre_save, sender=Product)
def track_price_changes(sender, instance, **kwargs):
    """
    Registra cambios en el precio de un producto
    """
    if instance.pk:  # Si el producto ya existe (no es nuevo)
        try:
            # Obtener el producto antes de la actualización
            old_instance = Product.objects.get(pk=instance.pk)
            
            # Si el precio ha cambiado, registrar en el historial
            if old_instance.price != instance.price:
                PriceHistory.objects.create(
                    product=instance,
                    price=instance.price
                )
        except Product.DoesNotExist:
            pass