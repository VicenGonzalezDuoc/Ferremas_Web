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
    def item_count(self):
        return self.cartitem_set.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def total(self):
        from django.db.models import F, Sum, DecimalField
        from django.db.models.functions import Cast
        
        result = self.cartitem_set.annotate(
            item_total=Cast(F('quantity') * F('product__price'), DecimalField())
        ).aggregate(total=Sum('item_total'))
        
        return result['total'] or 0
    
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
