from shop.models import Category

def categories(request):
    """
    Context processor para añadir las categorías a todas las plantillas
    """
    return {
        'categories': Category.objects.all()
    }

