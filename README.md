Diego Maldonado | Vicente Gonzalez

## Descripción del proyecto

Este es un proyecto de desarrollo web para una página de venta de productos de ferretería. Utiliza Django como framework principal y su ORM para la gestión de datos. Está conectado a una base de datos alojada en Firebase.

Además, el sistema integra:

- **Transbank Webpay** para pagos en línea.
- **Google reCAPTCHA** para la validación de usuarios.
- **WhatsApp Business API** para contacto directo con clientes.

## Levantar el proyecto

1. Clonar
```bash
git clone https://github.com/ReDiego0/Ferremas_Web.git
```

2. Crear entorno virtual y activarlo
```bash
python -m venv venv
./venv/Scripts/activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Iniciar el servidor
```bash
python manage.py runserver
```
