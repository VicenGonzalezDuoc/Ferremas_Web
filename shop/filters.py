import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    min_stock = django_filters.NumberFilter(field_name="stock", lookup_expr='gte')
    max_stock = django_filters.NumberFilter(field_name="stock", lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = {
            'code': ['exact', 'icontains'],
            'name': ['icontains'],
            'description': ['icontains'],
            'subcategory': ['exact'],
            'subcategory__category': ['exact'],
        }
