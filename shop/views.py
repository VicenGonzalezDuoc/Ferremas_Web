from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm

# Create your views here.

# Home view
def home(request):
    context = {
        'title': 'Ferremas - Tienda de Ferretería',
        'featured_products': []  # You can populate this from Firebase
    }
    return render(request, 'home.html', context)

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
def user_login(request):
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
def user_logout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

# User Profile
@login_required
def profile(request):
    return render(request, 'shop/profile.html', {'title': 'Mi Perfil'})
