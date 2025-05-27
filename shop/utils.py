from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para la API
    """
    # Primero, obtener la respuesta estándar
    response = exception_handler(exc, context)
    
    # Si no hay respuesta, es un error no manejado
    if response is None:
        logger.error(f"Error no manejado: {str(exc)}")
        return Response(
            {"error": "Se produjo un error interno en el servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Registrar el error
    logger.error(f"Error API: {str(exc)}")
    
    return response

