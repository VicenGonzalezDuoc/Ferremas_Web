from django.contrib import admin
from .models import Product, Category, Subcategory, Cart, CartItem
import uuid
from django.db import connection
from django.contrib import messages

class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price', 'stock', 'get_subcategory')
    search_fields = ('code', 'name')
    list_filter = ('subcategory__category', 'subcategory')
    
    def get_subcategory(self, obj):
        return obj.subcategory.name if obj.subcategory else "Sin categoría"
    get_subcategory.short_description = 'Subcategoría'
    
    def delete_model(self, request, obj):
        """
        Sobrescribe el método para manejar la eliminación de productos con UUIDs inválidos
        """
        try:
            # Intentar eliminar normalmente
            obj.delete()
        except ValueError:
            # Si hay un error con el UUID, usar SQL directo
            product_id = obj.id
            
            # Eliminar referencias en CartItem
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_cartitem WHERE product_id = %s",
                    [product_id]
                )
            
            # Eliminar el producto
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_product WHERE id = %s",
                    [product_id]
                )
            
            messages.success(request, "Producto eliminado exitosamente.")
    
    def delete_queryset(self, request, queryset):
        """
        Sobrescribe el método para manejar la eliminación masiva de productos
        """
        try:
            # Intentar eliminar normalmente
            queryset.delete()
        except ValueError:
            # Si hay un error, eliminar uno por uno
            for obj in queryset:
                try:
                    obj.delete()
                except ValueError:
                    # Si hay un error con el UUID, usar SQL directo
                    product_id = obj.id
                    
                    # Eliminar referencias en CartItem
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "DELETE FROM shop_cartitem WHERE product_id = %s",
                            [product_id]
                        )
                    
                    # Eliminar el producto
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "DELETE FROM shop_product WHERE id = %s",
                            [product_id]
                        )
                        messages.success(request, f"Producto {product_id} eliminado exitosamente.")

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at', 'item_count', 'total')
    search_fields = ('id', 'user__username', 'session_id')
    
    def get_queryset(self, request):
        """
        Sobrescribe el método para manejar carritos con UUIDs inválidos
        """
        try:
            # Intentar obtener el queryset normalmente
            return super().get_queryset(request)
        except ValueError:
            # Si hay un error con los UUIDs, usar SQL directo
            from django.db import models
            
            # Obtener los IDs de carritos válidos
            valid_cart_ids = []
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM shop_cart")
                rows = cursor.fetchall()
            
            for row in rows:
                cart_id = row[0]
                try:
                    uuid.UUID(str(cart_id))
                    valid_cart_ids.append(cart_id)
                except (ValueError, AttributeError):
                    pass
            
            # Devolver solo los carritos con UUIDs válidos
            return super().get_queryset(request).filter(id__in=valid_cart_ids)
    
    def delete_model(self, request, obj):
        """
        Sobrescribe el método para manejar la eliminación de carritos con UUIDs inválidos
        """
        try:
            # Intentar eliminar normalmente
            obj.delete()
        except ValueError:
            # Si hay un error con el UUID, usar SQL directo
            cart_id = obj.id
            
            # Eliminar referencias en CartItem
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_cartitem WHERE cart_id = %s",
                    [cart_id]
                )
            
            # Eliminar el carrito
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM shop_cart WHERE id = %s",
                    [cart_id]
                )
            
            messages.success(request, "Carrito eliminado exitosamente.")

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
