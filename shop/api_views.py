from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from .models import Product, Category
from .serializers import ProductSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint
    """
    return Response({
        'test': reverse('api-test', request=request, format=format),
        'products': '/api/products/',  # Placeholder for future product API
    })

@api_view(['GET'])
def api_test(request):
    """
    Test endpoint to verify API is working
    """
    return Response({
        'message': 'API is working!',
        'status': 'OK'
    })


