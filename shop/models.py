import uuid
from django.db import models
from django.contrib.auth.models import User

class Meta:
    permissions = [
        ("api_access", "Can access the API endpoints"),
    ]

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Subcategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Subcategories"
        unique_together = ('category', 'slug')

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # No añadir el campo featured aquí a menos que hagas migraciones
    
    def get_image_url(self):
        """
        Retorna la URL de la imagen del producto.
        Prioriza la imagen cargada, luego la URL externa.
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
    
    def save(self, *args, **kwargs):
        # Asegurarse de que el ID sea un UUID válido
        if not self.id:
            self.id = uuid.uuid4()
        elif not isinstance(self.id, uuid.UUID):
            try:
                self.id = uuid.UUID(str(self.id))
            except (ValueError, AttributeError):
                self.id = uuid.uuid4()
        
        # Generar código automáticamente si está vacío
        if not self.code:
            # Usar los primeros 8 caracteres del UUID como código
            self.code = f"FER-{str(self.id)[:8].upper()}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Carrito {self.id}"
    
    @property
    def items(self):
        """Devuelve los items del carrito"""
        return self.cartitem_set.all()
    
    @property
    def item_count(self):
        """Devuelve el número total de items en el carrito"""
        return self.cartitem_set.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def total(self):
        """Devuelve el total del carrito"""
        return sum(item.subtotal for item in self.items)
    
    def get_total_in_clp(self):
        """Obtiene el total del carrito en pesos chilenos"""
        return self.total
    
    def save(self, *args, **kwargs):
        # Asegurarse de que session_id sea una cadena
        if self.session_id is not None and not isinstance(self.session_id, str):
            self.session_id = str(self.session_id)
        
        # Asegurarse de que user sea un objeto User válido o None
        if self.user is not None and not isinstance(self.user, User):
            self.user = None
            
        super().save(*args, **kwargs)

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.product.price

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historial de precio'
        verbose_name_plural = 'Historiales de precios'
    
    def __str__(self):
        return f"{self.product.name} - ${self.price} ({self.created_at.strftime('%d/%m/%Y')})"

# Definir ShippingAddress antes de Order
class ShippingAddress(models.Model):
    """Modelo para las direcciones de envío"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    order_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dirección de Envío"
        verbose_name_plural = "Direcciones de Envío"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address}, {self.city}"
    
    def save(self, *args, **kwargs):
        # Si esta dirección se marca como predeterminada, desmarcar las demás
        if self.is_default:
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

# Ahora definir Order después de ShippingAddress
class Order(models.Model):
    """Modelo para los pedidos"""
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.order_number}"
    
    @property
    def get_total(self):
        """Obtiene el total del pedido"""
        return self.order_total


class OrderItem(models.Model):
    """Modelo para items de una orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()  # Precio en CLP
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
    
    @property
    def get_total(self):
        """Retorna el total del item"""
        return self.price * self.quantity


class Payment(models.Model):
    """Modelo para los pagos"""
    STATUS_CHOICES = (
        ('INITIALIZED', 'Inicializado'),
        ('AUTHORIZED', 'Autorizado'),
        ('FAILED', 'Fallido'),
        ('NULLIFIED', 'Anulado'),
        ('REVERSED', 'Reversado'),
        ('PARTIAL_REFUND', 'Reembolso Parcial'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100)
    token = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INITIALIZED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pago {self.payment_id} - {self.status}"
