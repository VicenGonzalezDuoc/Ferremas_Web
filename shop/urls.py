from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Category and product URLs
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('product/code/<str:product_code>/', views.product_by_code, name='product_by_code'),
    
    # Contact page
    path('contacto/', views.contact, name='contact'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<uuid:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<uuid:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # User URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    
    # Search URL
    path('search/', views.search_products, name='search'),
    # Añadir esta URL a las URLs existentes
    path('set-currency/', views.set_currency, name='set_currency'),
]








