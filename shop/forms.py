from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Category, Subcategory, Order, ShippingAddress

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a los campos
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'price', 'image', 'image_url', 'stock', 'subcategory']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para generar automáticamente'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://ejemplo.com/imagen.jpg'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'name', 'slug']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, label="Teléfono", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, label="Asunto", widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label="Mensaje", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class CheckoutForm(forms.ModelForm):
    """Formulario para la dirección de envío durante el checkout"""
    class Meta:
        model = ShippingAddress
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'region', 'order_note']
        widgets = {
            'order_note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Instrucciones especiales para la entrega'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'city': 'Ciudad',
            'region': 'Región',
            'order_note': 'Notas del pedido',
        }

class OrderForm(forms.ModelForm):
    """Formulario para crear órdenes"""
    class Meta:
        model = Order
        fields = ['order_total', 'shipping_cost']
        widgets = {
            'order_total': forms.HiddenInput(),
            'shipping_cost': forms.HiddenInput(),
        }

