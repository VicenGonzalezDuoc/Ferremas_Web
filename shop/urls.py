from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # URLs para categorías y productos
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('product/code/<str:product_code>/', views.product_by_code, name='product_by_code'),
    
    # Contact page
    path('contacto/', views.contact, name='contact'),
    
    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<uuid:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<uuid:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    
    # URLs para autenticación
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    
    # Search URL
    path('search/', views.search_products, name='search'),
    # Añadir esta URL a las URLs existentes
    path('set-currency/', views.set_currency, name='set_currency'),
    # URLs para el proceso de pago
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/confirmation/', views.payment_confirmation, name='payment_confirmation'),
    path('payment/complete/', views.payment_complete, name='payment_complete'),
]








