# Ferremas - Tienda de Ferretería Online

Diego Maldonado | Vicente Gonzalez

## Descripción del proyecto

Este es un proyecto de desarrollo web para una página de venta de productos de ferretería. Utiliza Django como framework principal y su ORM para la gestión de datos. Está conectado a una base de datos alojada en Firebase.

Además, el sistema integra:

- **Transbank Webpay** para pagos en línea.
- **Google reCAPTCHA** para la validación de usuarios.
- **WhatsApp Business API** para contacto directo con clientes.
- **API REST** para integración con sistemas externos.

## Requisitos previos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)
- Conexión a internet (para Firebase y Webpay)
- Git

## Levantar el proyecto

1. Clonar el repositorio
```bash
git clone https://github.com/ReDiego0/Ferremas_Web.git
cd Ferremas_Web
```

2. Crear entorno virtual y activarlo
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Crear archivo .env en la raíz del proyecto
Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```
# Django
SECRET_KEY=tu_clave_secreta_django
DEBUG=True

# Webpay (valores de prueba, reemplazar en producción)
WEBPAY_COMMERCE_CODE=597055555532
WEBPAY_API_KEY=579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
WEBPAY_ENVIRONMENT=TEST

# Firebase
FIREBASE_API_KEY=tu_api_key_de_firebase
FIREBASE_AUTH_DOMAIN=tu_proyecto.firebaseapp.com
FIREBASE_DATABASE_URL=https://tu_proyecto-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=tu_proyecto
FIREBASE_STORAGE_BUCKET=tu_proyecto.appspot.com
FIREBASE_MESSAGING_SENDER_ID=tu_sender_id
FIREBASE_APP_ID=tu_app_id
```

5. Aplicar migraciones
```bash
python manage.py migrate
```

6. Iniciar el servidor
```bash
python manage.py runserver
```

7. Acceder a la aplicación
Abre tu navegador y visita: http://127.0.0.1:8000/

## Dependencias principales

El proyecto utiliza las siguientes dependencias principales:

- Django 4.2.21
- Pyrebase4 (para Firebase)
- Django REST Framework (para la API)
- Transbank SDK (para pagos)
- Pillow (para manejo de imágenes)
- Python-dotenv (para variables de entorno)
- Crispy Forms con Bootstrap 5 (para formularios)

Puedes instalarlas manualmente con:

```bash
pip install django==4.2.21
pip install pyrebase4
pip install django-crispy-forms crispy-bootstrap5
pip install djangorestframework drf-yasg django-filter
pip install Pillow
pip install transbank-sdk==6.0.0
pip install python-dotenv
```

## Verificación de Transbank

Para verificar que Transbank está correctamente configurado, ejecuta:

```bash
python check_transbank_installation.py
```

Si hay problemas con Transbank, asegúrate de tener instalada la versión correcta:

```bash
pip install transbank-sdk==6.0.0
```

## Estructura del proyecto

- `Ferremas/`: Configuración principal del proyecto Django
- `shop/`: Aplicación principal con modelos, vistas y lógica de negocio
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `media/`: Archivos subidos por los usuarios
- `api/`: Endpoints de la API REST

## Acceso a la API

La API está documentada y disponible en:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- Documentación personalizada: `/api/docs/`

## Configuración de producción

Para configurar el proyecto en producción:

1. En el archivo `.env`:
   - Cambiar `DEBUG=False`
   - Establecer una `SECRET_KEY` segura
   - Cambiar `WEBPAY_ENVIRONMENT=PRODUCTION`
   - Actualizar las credenciales de Webpay con las de producción

2. Configurar un servidor web como Nginx o Apache

3. Usar Gunicorn o uWSGI como servidor WSGI

4. Configurar HTTPS con certificados SSL

## Solución de problemas comunes

### Problemas con Webpay

Si la página de Webpay se queda en blanco:
1. Verifica que la biblioteca Transbank esté correctamente instalada
2. Comprueba que las credenciales en el archivo `.env` sean correctas
3. Asegúrate de que la URL de retorno sea accesible desde internet en producción

### Problemas con Firebase

Si hay problemas de conexión con Firebase:
1. Verifica que las credenciales en el archivo `.env` sean correctas
2. Comprueba que las reglas de seguridad de Firebase permitan las operaciones

## Contacto y soporte

Para soporte técnico, contactar a:
- Email: soporte@ferremas.cl
- WhatsApp: +56 9 XXXX XXXX

