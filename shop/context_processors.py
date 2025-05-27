from .models import Category

def categories(request):
    """
    Añade las categorías al contexto de todas las plantillas
    """
    try:
        all_categories = Category.objects.all()
        return {
            'categories': all_categories
        }
    except Exception as e:
        # En caso de error, devolver una lista vacía para evitar errores en las plantillas
        print(f"Error en context_processor de categorías: {e}")
        return {
            'categories': []
        }


