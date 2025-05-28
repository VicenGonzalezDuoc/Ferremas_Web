from django.shortcuts import render
from django.views.generic import TemplateView
import pyrebase
from django.conf import settings

# Usar la configuración de Firebase desde settings
config = settings.FIREBASE_CONFIG

# Function-based view approach
def home(request):
    context = {
        'title': 'Ferremas - Tienda de Ferretería',
        'featured_products': []  # You can populate this from Firebase
    }
    return render(request, 'home.html', context)

# Class-based view approach
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ferremas - Tienda de Ferretería'
        context['featured_products'] = []  # You can populate this from Firebase
        return context
