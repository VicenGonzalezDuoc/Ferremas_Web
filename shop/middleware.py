class CurrencyMiddleware:
    """
    Middleware para manejar la divisa actual
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Asegurarse de que la divisa esté disponible en la sesión
        if 'currency' not in request.session:
            request.session['currency'] = 'CLP'
        
        # Procesar la solicitud
        response = self.get_response(request)
        
        return response