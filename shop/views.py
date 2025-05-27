import logging
import traceback
import sys
import inspect

logger = logging.getLogger(__name__)

def debug_uuid_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, AttributeError) as e:
            if "badly formed hexadecimal UUID string" in str(e) or "'int' object has no attribute 'replace'" in str(e):
                # Obtener el traceback completo
                tb = traceback.extract_tb(sys.exc_info()[2])
                
                # Imprimir información detallada
                logger.error(f"UUID Error en {func.__name__}: {e}")
                logger.error(f"Traceback completo: {tb}")
                
                # Imprimir los argumentos de la función
                frame = inspect.currentframe()
                try:
                    logger.error(f"Argumentos de la función: {args}, {kwargs}")
                    
                    # Imprimir variables locales
                    for i, frame_info in enumerate(inspect.getouterframes(frame)):
                        if i < 5:  # Limitar a 5 frames para no sobrecargar
                            logger.error(f"Frame {i}, función {frame_info.function}:")
                            for key, value in frame_info.frame.f_locals.items():
                                logger.error(f"  {key} = {repr(value)}")
                finally:
                    del frame
                
                # Imprimir en la consola para depuración inmediata
                print(f"UUID Error en {func.__name__}: {e}")
                print(f"Traceback completo: {tb}")
                
                # Crear un carrito temporal para evitar errores
                if func.__name__ == 'home':
                    request = args[0]
                    if request.user.is_authenticated:
                        cart = Cart.objects.create(user=request.user)
                    else:
                        cart = Cart.objects.create(session_id="temp_session")
                    
                    context = {
                        'title': 'Ferremas - Tienda de Ferretería',
                        'categories': Category.objects.all(),
                        'featured_products': [],
                        'cart': cart,
                    }
                    return render(request, 'shop/home.html', context)
            raise
    return wrapper

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .forms import UserRegisterForm, UserLoginForm, ProductForm, CategoryForm, SubcategoryForm, ContactForm
from .models import Product, Cart, CartItem, Category, Subcategory
import uuid
from django.views.decorators.cache import cache_page
from django.utils.cache import patch_vary_headers

def has_api_access(user):
    """Verifica si el usuario tiene acceso a la API"""
    return user.is_staff or user.has_perm('shop.api_access')

@login_required
def api_access_denied(request):
    """Vista para mostrar mensaje de acceso denegado a la API"""
    return render(request, 'shop/api_access_denied.html')

# Create your views here.

# Get or create cart for the current user/session
def get_or_create_cart(request):
    """Obtiene o crea un carrito para el usuario actual"""
    try:
        if request.user.is_authenticated:
            # Intentar obtener el carrito existente del usuario
            try:
                cart = Cart.objects.get(user=request.user)
                
                # Si el usuario tiene un carrito de sesión, transferir los items
                if hasattr(request, 'session') and request.session.session_key:
                    try:
                        session_cart = Cart.objects.get(session_id=request.session.session_key)
                        if session_cart.id != cart.id:  # Evitar duplicación
                            # Transferir items del carrito de sesión al carrito de usuario
                            for item in session_cart.cartitem_set.all():
                                # Verificar si el producto ya está en el carrito del usuario
                                user_item, created = CartItem.objects.get_or_create(
                                    cart=cart,
                                    product=item.product,
                                    defaults={'quantity': item.quantity}
                                )
                                if not created:
                                    user_item.quantity += item.quantity
                                    user_item.save()
                            
                            # Eliminar el carrito de sesión
                            session_cart.delete()
                    except Cart.DoesNotExist:
                        pass
                
                return cart
            except Cart.DoesNotExist:
                # Crear un nuevo carrito para el usuario
                return Cart.objects.create(user=request.user)
        else:
            # Usuario no autenticado, usar sesión
            if not hasattr(request, 'session') or not request.session.session_key:
                request.session.create()
            
            session_id = request.session.session_key
            try:
                # Intentar obtener el carrito existente de la sesión
                return Cart.objects.get(session_id=session_id)
            except Cart.DoesNotExist:
                # Crear un nuevo carrito para la sesión
                return Cart.objects.create(session_id=session_id)
    except Exception as e:
        # Registrar el error y crear un carrito temporal
        logger.error(f"Error en get_or_create_cart: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Crear un carrito temporal
        if request.user.is_authenticated:
            return Cart.objects.create(user=request.user)
        else:
            temp_session = getattr(request, 'session', None)
            session_id = getattr(temp_session, 'session_key', "temp_session")
            return Cart.objects.create(session_id=session_id)

# Home view
def home(request):
    """View for home page"""
    # Obtener categorías
    categories = Category.objects.all()
    
    # Obtener productos destacados (usando los más recientes con stock disponible)
    try:
        featured_products = Product.objects.filter(stock__gt=0).order_by('-created_at')[:8]
    except Exception as e:
        # En caso de error, mostrar lista vacía
        featured_products = []
        print(f"Error al obtener productos destacados: {e}")
    
    context = {
        'title': 'Ferremas - Tienda de Ferretería',
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'shop/home.html', context)

def home_alternative(request):
    """Vista alternativa para la página de inicio sin usar UUIDs directamente"""
    categories = Category.objects.all()
    
    # Crear un carrito temporal para evitar errores
    try:
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_id=session_id)
    except Exception as e:
        # Crear un carrito temporal si hay un error
        if request.user.is_authenticated:
            cart = Cart.objects.create(user=request.user)
        else:
            cart = Cart.objects.create(session_id="temp_session")
    
    # Obtener productos destacados (los más recientes con stock disponible)
    try:
        featured_products = Product.objects.filter(stock__gt=0).order_by('-created_at')[:8]
    except Exception as e:
        featured_products = []
    
    context = {
        'title': 'Ferremas - Tienda de Ferretería',
        'categories': categories,
        'featured_products': featured_products,
        'cart': cart,
    }
    
    return render(request, 'shop/home.html', context)

def category_detail(request, category_slug):
    """View for category detail page"""
    category = get_object_or_404(Category, slug=category_slug)
    subcategories = category.subcategories.all()
    cart = get_or_create_cart(request)
    
    # Get products directly associated with this category
    products = Product.objects.filter(subcategory__category=category)
    
    # Obtener todas las categorías para el menú desplegable
    all_categories = Category.objects.all()
    
    context = {
        'title': category.name,
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'cart': cart,
        'categories': all_categories,  # Añadir explícitamente las categorías al contexto
    }
    return render(request, 'shop/category_detail.html', context)

def subcategory_detail(request, category_slug, subcategory_slug):
    """View for subcategory detail page"""
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug, category=category)
    cart = get_or_create_cart(request)
    
    # Get products in this subcategory
    products = Product.objects.filter(subcategory=subcategory)
    
    # Obtener todas las categorías para el menú desplegable
    all_categories = Category.objects.all()
    
    context = {
        'title': subcategory.name,
        'category': category,
        'subcategory': subcategory,
        'products': products,
        'cart': cart,
        'categories': all_categories,  # Añadir explícitamente las categorías al contexto
    }
    return render(request, 'shop/subcategory_detail.html', context)

def product_detail(request, product_id):
    """View for product detail page"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    context = {
        'title': product.name,
        'product': product,
        'cart': cart,
    }
    return render(request, 'shop/product_detail.html', context)

def product_by_code(request, product_code):
    """Redirect to product detail page using product code"""
    product = get_object_or_404(Product, code=product_code)
    return redirect('product_detail', product_id=product.id)

# User Registration
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {user.username}')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'shop/register.html', {'form': form, 'title': 'Registro'})

# User Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido de nuevo, {username}!')
                return redirect('home')
    else:
        form = UserLoginForm()
    
    return render(request, 'shop/login.html', {'form': form, 'title': 'Iniciar Sesión'})

# User Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

# User Profile
@login_required
def profile(request):
    """Vista para el perfil del usuario"""
    # Obtener o crear un carrito para el usuario
    cart = get_or_create_cart(request)
    
    context = {
        'title': 'Mi Perfil',
        'cart': cart,
    }
    return render(request, 'shop/profile.html', context)

# View cart
def cart_view(request):
    """View for shopping cart"""
    cart = get_or_create_cart(request)
    
    context = {
        'title': 'Carrito de Compras',
        'cart': cart,
        'cart_items': cart.cartitem_set.all()
    }
    response = render(request, 'shop/cart.html', context)
    patch_vary_headers(response, ["Cookie"])
    return response

# Add to cart
@debug_uuid_error
def add_to_cart(request, product_id):
    """Añade un producto al carrito de compras"""
    try:
        # Convertir product_id a UUID si es una cadena
        if isinstance(product_id, str):
            try:
                product_id = uuid.UUID(product_id)
            except ValueError:
                # Si no es un UUID válido, intentar buscar por código
                product = get_object_or_404(Product, code=product_id)
                product_id = product.id
        
        # Obtener el producto
        product = get_object_or_404(Product, id=product_id)
        
        # Verificar stock
        if product.stock <= 0:
            messages.warning(request, f'Lo sentimos, {product.name} está agotado.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        # Obtener o crear el carrito
        cart = get_or_create_cart(request)
        
        # Verificar si el producto ya está en el carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        # Si el producto ya existe, aumentar la cantidad
        if not created:
            # Verificar que no exceda el stock disponible
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f'Se actualizó la cantidad de {product.name} en el carrito.')
            else:
                messages.warning(request, f'No hay suficiente stock de {product.name}.')
        else:
            messages.success(request, f'{product.name} añadido al carrito.')
        
        # Manejar solicitudes AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.item_count,
                'message': f'{product.name} añadido al carrito.'
            })
        
        # Redirigir a la página anterior o al carrito
        referer = request.META.get('HTTP_REFERER')
        if referer and 'add_to_cart' not in referer:
            response = redirect(referer)
        else:
            response = redirect('cart')
        
        patch_vary_headers(response, ["Cookie"])
        return response
        
    except Exception as e:
        logger.error(f"Error al añadir producto al carrito: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, f"Error al añadir producto al carrito. Por favor, inténtelo de nuevo.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

# Update cart item quantity
@debug_uuid_error
def update_cart(request, item_id):
    """Actualiza la cantidad de un producto en el carrito"""
    try:
        # Convertir a UUID si es necesario
        if isinstance(item_id, str):
            try:
                item_id = uuid.UUID(item_id)
            except ValueError:
                pass
        
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Check if user owns this cart item
        if request.user.is_authenticated:
            # Verificar si el usuario es dueño del carrito
            if cart_item.cart.user and cart_item.cart.user != request.user:
                messages.error(request, "No tienes permiso para modificar este carrito.")
                return redirect('cart')
        else:
            # Verificar si la sesión es dueña del carrito
            session_id = request.session.session_key
            if cart_item.cart.session_id and cart_item.cart.session_id != session_id:
                messages.error(request, "No tienes permiso para modificar este carrito.")
                return redirect('cart')
        
        # Get quantity from POST data
        quantity = int(request.POST.get('quantity', 1))
        
        # Verificar stock disponible
        if quantity > cart_item.product.stock:
            messages.warning(request, f"Solo hay {cart_item.product.stock} unidades disponibles de {cart_item.product.name}.")
            quantity = cart_item.product.stock
        
        # Update quantity
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Carrito actualizado.")
        else:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} eliminado del carrito.')
        
        # Manejar solicitudes AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart_item.cart.item_count,
                'item_subtotal': float(cart_item.subtotal) if quantity > 0 else 0,
                'cart_total': float(cart_item.cart.total),
                'message': "Carrito actualizado."
            })
        
        return redirect('cart')
    except Exception as e:
        logger.error(f"Error al actualizar carrito: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, f"Error al actualizar carrito: {str(e)}")
        return redirect('cart')

# Remove from cart
@debug_uuid_error
def remove_from_cart(request, item_id):
    """Elimina un producto del carrito"""
    try:
        # Convertir a UUID si es necesario
        if isinstance(item_id, str):
            try:
                item_id = uuid.UUID(item_id)
            except ValueError:
                pass
        
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Verificar permisos
        if request.user.is_authenticated:
            if cart_item.cart.user and cart_item.cart.user != request.user:
                messages.error(request, "No tienes permiso para modificar este carrito.")
                return redirect('cart')
        else:
            session_id = request.session.session_key
            if cart_item.cart.session_id and cart_item.cart.session_id != session_id:
                messages.error(request, "No tienes permiso para modificar este carrito.")
                return redirect('cart')
        
        cart = cart_item.cart
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.success(request, f'{product_name} eliminado del carrito.')
        
        # Manejar solicitudes AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.item_count,
                'cart_total': float(cart.total),
                'message': f'{product_name} eliminado del carrito.'
            })
        
        return redirect('cart')
    except Exception as e:
        logger.error(f"Error al eliminar producto del carrito: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, f"Error al eliminar producto del carrito: {str(e)}")
        return redirect('cart')

# Clear cart
def clear_cart(request):
    cart = get_or_create_cart(request)
    cart.cartitem_set.all().delete()
    messages.success(request, "Carrito vaciado.")
    return redirect('cart')

# Admin product management views
@login_required
def product_list(request):
    """View for listing all products (admin only)"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    products = Product.objects.all()
    context = {
        'title': 'Administrar Productos',
        'products': products
    }
    return render(request, 'shop/admin/product_list.html', context)

@login_required
def product_create(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado exitosamente.")
            return redirect('product_list')
    else:
        form = ProductForm()
    
    context = {
        'title': 'Crear Producto',
        'form': form
    }
    return render(request, 'shop/admin/product_form.html', context)

@login_required
def product_edit(request, product_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    try:
        # Convertir a UUID si es necesario
        if not isinstance(product_id, uuid.UUID):
            try:
                product_id = uuid.UUID(str(product_id))
            except ValueError:
                # Si no es un UUID válido, buscar por código
                product = get_object_or_404(Product, code=product_id)
                product_id = product.id
        
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Producto actualizado exitosamente.")
                return redirect('product_list')
        else:
            form = ProductForm(instance=product)
        
        context = {
            'title': 'Editar Producto',
            'form': form,
            'product': product
        }
        return render(request, 'shop/admin/product_form.html', context)
    except Exception as e:
        messages.error(request, f"Error al editar producto: {str(e)}")
        return redirect('product_list')

@login_required
def product_delete(request, product_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    try:
        # Intentar obtener el producto normalmente
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == 'POST':
            # Eliminar manualmente los items del carrito relacionados
            CartItem.objects.filter(product=product).delete()
            
            # Eliminar el producto
            product.delete()
            messages.success(request, "Producto eliminado exitosamente.")
            return redirect('product_list')
        
        context = {
            'title': 'Eliminar Producto',
            'product': product
        }
        return render(request, 'shop/admin/product_confirm_delete.html', context)
    except ValueError:
        # Si hay un error con el UUID, usar SQL directo
        if request.method == 'POST':
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
            return redirect('product_list')
        
        # Para la vista de confirmación, obtener datos del producto directamente
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM shop_product WHERE id = %s",
                [product_id]
            )
            product_data = cursor.fetchone()
        
        if product_data:
            context = {
                'title': 'Eliminar Producto',
                'product': {'id': product_id, 'name': product_data[0]}
            }
            return render(request, 'shop/admin/product_confirm_delete.html', context)
        else:
            messages.error(request, "Producto no encontrado.")
            return redirect('product_list')

# Category management views
@login_required
def category_list(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    categories = Category.objects.all()
    context = {
        'title': 'Administrar Categorías',
        'categories': categories
    }
    return render(request, 'shop/admin/category_list.html', context)

@login_required
def category_create(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada exitosamente.")
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {
        'title': 'Crear Categoría',
        'form': form
    }
    return render(request, 'shop/admin/category_form.html', context)

@login_required
def category_edit(request, category_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada exitosamente.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'title': 'Editar Categoría',
        'form': form,
        'category': category
    }
    return render(request, 'shop/admin/category_form.html', context)

# Subcategory management views
@login_required
def subcategory_list(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    subcategories = Subcategory.objects.all()
    context = {
        'title': 'Administrar Subcategorías',
        'subcategories': subcategories
    }
    return render(request, 'shop/admin/subcategory_list.html', context)

@login_required
def subcategory_create(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subcategoría creada exitosamente.")
            return redirect('subcategory_list')
    else:
        form = SubcategoryForm()
    
    context = {
        'title': 'Crear Subcategoría',
        'form': form
    }
    return render(request, 'shop/admin/subcategory_form.html', context)

@login_required
def subcategory_edit(request, subcategory_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')
    
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, "Subcategoría actualizada exitosamente.")
            return redirect('subcategory_list')
    else:
        form = SubcategoryForm(instance=subcategory)
    
    context = {
        'title': 'Editar Subcategoría',
        'form': form,
        'subcategory': subcategory
    }
    return render(request, 'shop/admin/subcategory_form.html', context)

def contact(request):
    """View for contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Procesar el formulario
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Aquí puedes agregar código para enviar el email
            # Por ejemplo, usando send_mail de Django
            
            # Mostrar mensaje de éxito
            messages.success(request, 'Tu mensaje ha sido enviado correctamente. Nos pondremos en contacto contigo pronto.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'title': 'Contacto',
        'form': form,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Reemplaza con tu clave API de Google Maps
    }
    return render(request, 'shop/contact.html', context)

def api_docs(request):
    """
    Vista para la documentación personalizada de la API
    """
    # Verificar si el usuario tiene permisos para acceder a la API
    if not request.user.is_authenticated or not request.user.is_staff:
        return render(request, 'shop/api_access_denied.html')
        
    context = {
        'title': 'Documentación de la API de Ferremas',
    }
    return render(request, 'shop/api_docs.html', context)

def debug_view(request):
    """Vista de depuración para identificar problemas con UUIDs"""
    try:
        # Intentar crear un carrito
        if request.user.is_authenticated:
            # Verificar que el usuario sea válido
            try:
                user = User.objects.get(pk=request.user.pk)
                cart = Cart.objects.create(user=user)
            except Exception as e:
                # Si hay un error con el usuario, crear un carrito sin usuario
                cart = Cart.objects.create(session_id="debug_session")
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart = Cart.objects.create(session_id=session_id)
        
        # Intentar crear un producto
        try:
            category = Category.objects.first()
            if not category:
                category = Category.objects.create(name="Categoría de prueba")
            
            subcategory = Subcategory.objects.filter(category=category).first()
            if not subcategory:
                subcategory = Subcategory.objects.create(name="Subcategoría de prueba", category=category)
            
            product = Product.objects.create(
                name="Producto de prueba",
                description="Descripción de prueba",
                price=100.00,
                stock=10,
                subcategory=subcategory
            )
            
            # Intentar añadir el producto al carrito
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1
            )
            
            # Devolver información de depuración
            return JsonResponse({
                'success': True,
                'cart_id': str(cart.id),
                'product_id': str(product.id),
                'product_code': product.code if hasattr(product, 'code') else None,
                'cart_item_id': str(cart_item.id)
            })
        except Exception as e:
            # Si hay un error con el producto, devolver información del carrito
            return JsonResponse({
                'success': True,
                'cart_id': str(cart.id),
                'error_product': str(e)
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

def custom_404(request, exception):
    """Vista personalizada para manejar errores 404"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Vista personalizada para manejar errores 500"""
    return render(request, '500.html', status=500)

def db_diagnosis(request):
    """Vista para diagnosticar problemas en la base de datos"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        # Verificar la estructura de la tabla Cart
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(shop_cart)")
            cart_columns = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) FROM shop_cart")
            cart_count = cursor.fetchone()[0]
            
            # Obtener algunos carritos para diagnóstico
            cursor.execute("SELECT id, user_id, session_id FROM shop_cart LIMIT 10")
            cart_samples = cursor.fetchall()
            
            # Verificar si hay carritos con tipos de datos incorrectos
            cursor.execute("SELECT id, user_id, session_id FROM shop_cart WHERE user_id IS NOT NULL AND typeof(user_id) != 'integer'")
            invalid_user_carts = cursor.fetchall()
            
            cursor.execute("SELECT id, user_id, session_id FROM shop_cart WHERE session_id IS NOT NULL AND typeof(session_id) != 'text'")
            invalid_session_carts = cursor.fetchall()
        
        return JsonResponse({
            'success': True,
            'cart_columns': cart_columns,
            'cart_count': cart_count,
            'cart_samples': cart_samples,
            'invalid_user_carts': invalid_user_carts,
            'invalid_session_carts': invalid_session_carts
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

def clean_database(request):
    """Vista para limpiar datos corruptos en la base de datos"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        # Eliminar carritos con datos incorrectos
        from django.db import connection
        with connection.cursor() as cursor:
            # Identificar carritos con user_id inválido
            cursor.execute("SELECT id FROM shop_cart WHERE user_id IS NOT NULL AND typeof(user_id) != 'integer'")
            invalid_user_carts = [row[0] for row in cursor.fetchall()]
            
            # Identificar carritos con session_id inválido
            cursor.execute("SELECT id FROM shop_cart WHERE session_id IS NOT NULL AND typeof(session_id) != 'text'")
            invalid_session_carts = [row[0] for row in cursor.fetchall()]
            
            # Eliminar carritos inválidos
            for cart_id in invalid_user_carts + invalid_session_carts:
                cursor.execute("DELETE FROM shop_cartitem WHERE cart_id = ?", [cart_id])
                cursor.execute("DELETE FROM shop_cart WHERE id = ?", [cart_id])
        
        return JsonResponse({
            'success': True,
            'deleted_user_carts': len(invalid_user_carts),
            'deleted_session_carts': len(invalid_session_carts)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

def search_products(request):
    """Vista para buscar productos"""
    query = request.GET.get('q', '')
    
    if query:
        # Buscar en nombre, descripción y código
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(code__icontains=query)
        ).filter(stock__gt=0)
    else:
        products = Product.objects.none()
    
    # Crear un carrito para el usuario
    cart = get_or_create_cart(request)
    
    context = {
        'title': f'Resultados para "{query}"',
        'query': query,
        'products': products,
        'cart': cart,
    }
    
    return render(request, 'shop/search_results.html', context)

@login_required
def orders(request):
    """Vista para los pedidos del usuario"""
    # Crear un carrito para el usuario
    cart = get_or_create_cart(request)
    
    # Aquí puedes añadir la lógica para obtener los pedidos del usuario
    # Por ahora, solo devolvemos una plantilla básica
    
    context = {
        'title': 'Mis Pedidos',
        'cart': cart,
    }
    return render(request, 'shop/orders.html', context)
