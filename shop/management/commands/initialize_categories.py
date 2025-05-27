from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Subcategory

class Command(BaseCommand):
    help = 'Initialize categories and subcategories for Ferremas'

    def handle(self, *args, **options):
        # Define categories and subcategories
        categories_data = [
            {
                'name': 'Herramientas Manuales',
                'subcategories': ['Martillos', 'Destornilladores', 'Llaves']
            },
            {
                'name': 'Herramientas Eléctricas',
                'subcategories': ['Taladros', 'Sierras', 'Lijadoras']
            },
            {
                'name': 'Materiales de Construcción',
                'subcategories': ['Materiales Básicos', 'Cemento', 'Arena', 'Ladrillos']
            },
            {
                'name': 'Acabados',
                'subcategories': ['Pinturas', 'Barnices', 'Cerámicos']
            },
            {
                'name': 'Equipos de Seguridad',
                'subcategories': ['Cascos', 'Guantes', 'Lentes de Seguridad']
            },
            {
                'name': 'Accesorios Varios',
                'subcategories': ['Tornillos', 'Clavos', 'Adhesivos', 'Cintas']
            }
        ]
        
        # Create categories and subcategories
        for category_data in categories_data:
            category_name = category_data['name']
            category_slug = slugify(category_name)
            
            # Create or get category
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': category_slug}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(f'Category already exists: {category_name}')
            
            # Create subcategories
            for subcategory_name in category_data['subcategories']:
                subcategory_slug = slugify(subcategory_name)
                
                subcategory, subcategory_created = Subcategory.objects.get_or_create(
                    category=category,
                    name=subcategory_name,
                    defaults={'slug': subcategory_slug}
                )
                
                if subcategory_created:
                    self.stdout.write(self.style.SUCCESS(f'  - Created subcategory: {subcategory_name}'))
                else:
                    self.stdout.write(f'  - Subcategory already exists: {subcategory_name}')
        
        self.stdout.write(self.style.SUCCESS('Categories and subcategories initialized successfully!'))
