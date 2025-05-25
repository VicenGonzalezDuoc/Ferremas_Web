from django.shortcuts import render
from django.views.generic import TemplateView
import pyrebase

config={
    "apiKey": "AIzaSyD8ccAxOcOftM2KVcH28Di7rvpYW8Mp-nM",
    "authDomain": "ferremas-292f7.firebaseapp.com",
    "databaseURL": "https://ferremas-292f7-default-rtdb.firebaseio.com",
    "projectId": "ferremas-292f7",
    "storageBucket": "ferremas-292f7.firebasestorage.app",
    "messagingSenderId": "837938741466",
    "appId": "1:837938741466:web:2e63e016318b97ec2525e3",
}

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
