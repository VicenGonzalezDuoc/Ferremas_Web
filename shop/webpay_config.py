import logging
import importlib.util
import traceback
import sys
from django.conf import settings

logger = logging.getLogger(__name__)

# Obtener credenciales desde settings (que a su vez las obtiene de .env)
WEBPAY_COMMERCE_CODE = settings.WEBPAY_COMMERCE_CODE
WEBPAY_API_KEY = settings.WEBPAY_API_KEY
WEBPAY_PRODUCTION = settings.WEBPAY_PRODUCTION

# Verificar la instalación de Transbank
WEBPAY_AVAILABLE = False
Transaction = None
WebpayOptions = None
IntegrationType = None

# Intentar importar las clases necesarias
try:
    # Verificar la versión de Transbank
    try:
        import transbank
        print(f"Versión de Transbank SDK: {transbank.__version__}", file=sys.stderr)
    except (ImportError, AttributeError):
        print("No se pudo determinar la versión de Transbank SDK", file=sys.stderr)
    
    # Importar Transaction y WebpayOptions
    from transbank.webpay.webpay_plus.transaction import Transaction
    from transbank.webpay.webpay_plus.transaction import WebpayOptions
    from transbank.common.integration_type import IntegrationType
    
    # Probar si podemos crear una transacción
    options = WebpayOptions(WEBPAY_COMMERCE_CODE, WEBPAY_API_KEY, 
                           IntegrationType.LIVE if WEBPAY_PRODUCTION else IntegrationType.TEST)
    tx = Transaction(options)
    
    # Intentar crear una transacción de prueba
    try:
        response = tx.create("OC12345", "S12345", 1000, "http://localhost:8000/webpay/return")
        if isinstance(response, dict) and 'token' in response and 'url' in response:
            WEBPAY_AVAILABLE = True
            logger.info("Biblioteca Transbank verificada correctamente")
            print("Biblioteca Transbank verificada correctamente", file=sys.stderr)
        else:
            logger.error("La respuesta de la transacción no tiene el formato esperado")
            print(f"La respuesta de la transacción no tiene el formato esperado: {response}", file=sys.stderr)
    except Exception as e:
        logger.error(f"Error al crear transacción de prueba: {str(e)}")
        print(f"Error al crear transacción de prueba: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
except ImportError as e:
    logger.error(f"Error al importar clases de Transbank: {str(e)}")
    print(f"Error al importar clases de Transbank: {str(e)}", file=sys.stderr)
except Exception as e:
    logger.error(f"Error al verificar la biblioteca Transbank: {str(e)}")
    logger.error(traceback.format_exc())
    print(f"Error al verificar la biblioteca Transbank: {str(e)}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)

# Si Transbank no está disponible, crear clases simuladas
if not WEBPAY_AVAILABLE:
    logger.warning("Usando implementación simulada de Transbank")
    print("Usando implementación simulada de Transbank", file=sys.stderr)
    
    class IntegrationType:
        TEST = "TEST"
        LIVE = "LIVE"
    
    class WebpayOptions:
        def __init__(self, commerce_code, api_key, integration_type):
            self.commerce_code = commerce_code
            self.api_key = api_key
            self.integration_type = integration_type
    
    class Transaction:
        def __init__(self, options):
            self.options = options
        
        def create(self, buy_order, session_id, amount, return_url):
            return {"token": "dummy_token", "url": "/"}
        
        def commit(self, token):
            return {
                "status": "AUTHORIZED",
                "response_code": 0,
                "amount": 1000,
                "buy_order": "dummy_order",
                "session_id": "dummy_session",
                "card_detail": {"card_number": "XXXX-XXXX-XXXX-6623"},
                "accounting_date": "0413",
                "transaction_date": "2023-04-13T16:15:23.863Z",
                "authorization_code": "1213",
                "payment_type_code": "VN",
                "installments_number": 0,
                "installments_amount": 0,
                "balance": 0
            }

def get_transaction_options(production=None):
    """
    Obtiene las opciones para crear una transacción
    
    Args:
        production (bool): Si es True, usa credenciales de producción.
                          Si es None, usa el valor de settings.WEBPAY_PRODUCTION
    
    Returns:
        WebpayOptions: Opciones para crear una transacción
    """
    if production is None:
        production = WEBPAY_PRODUCTION
        
    # Configurar para producción o pruebas según corresponda
    commerce_code = WEBPAY_COMMERCE_CODE
    api_key = WEBPAY_API_KEY
    integration_type = IntegrationType.LIVE if production else IntegrationType.TEST
    
    return WebpayOptions(commerce_code, api_key, integration_type)

def configure_webpay(production=False):
    """
    Configura la integración con Webpay
    
    Args:
        production (bool): Si es True, usa credenciales de producción
    """
    if not WEBPAY_AVAILABLE:
        logger.warning("La biblioteca de Transbank no está instalada. La funcionalidad de pago estará limitada.")
        return False
    
    try:
        # En la versión 6.0.0, la configuración se hace al crear la instancia de Transaction
        # con el objeto Options, así que esta función ya no es necesaria.
        logger.info(f"Webpay configurado correctamente en modo {'producción' if production else 'integración'}")
        return True
    except Exception as e:
        logger.error(f"Error al configurar Webpay: {str(e)}")
        return False


















