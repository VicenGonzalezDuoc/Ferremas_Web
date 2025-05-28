import sys
import traceback

def check_transbank_installation():
    """
    Verifica la instalación de la biblioteca Transbank
    """
    print("Verificando instalación de Transbank...")
    
    try:
        # Verificar si la biblioteca está instalada
        import transbank
        print(f"✅ Biblioteca Transbank instalada")
        
        # Verificar la versión
        try:
            print(f"   Versión: {transbank.__version__}")
        except AttributeError:
            print("   No se pudo determinar la versión")
        
        # Verificar si podemos importar las clases necesarias
        try:
            from transbank.webpay.webpay_plus.transaction import Transaction
            print("✅ Se pudo importar Transaction")
            
            from transbank.webpay.webpay_plus.transaction import WebpayOptions
            print("✅ Se pudo importar WebpayOptions")
            
            from transbank.common.integration_type import IntegrationType
            print("✅ Se pudo importar IntegrationType")
            
            # Probar si podemos crear una transacción
            options = WebpayOptions("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C", IntegrationType.TEST)
            tx = Transaction(options)
            print("✅ Se pudo crear una instancia de Transaction")
            
            # Intentar crear una transacción de prueba
            try:
                response = tx.create("OC12345", "S12345", 1000, "http://localhost:8000/webpay/return")
                print("✅ Se pudo crear una transacción de prueba")
                print(f"   Respuesta: {response}")
                
                if isinstance(response, dict) and 'token' in response and 'url' in response:
                    print("✅ La respuesta tiene el formato esperado")
                    print(f"   Token: {response['token']}")
                    print(f"   URL: {response['url']}")
                else:
                    print("❌ La respuesta no tiene el formato esperado")
                
                return True
            except Exception as e:
                print(f"❌ Error al crear transacción de prueba: {str(e)}")
                print(traceback.format_exc())
                return False
        except ImportError as e:
            print(f"❌ Error al importar clases de Transbank: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error al verificar la biblioteca Transbank: {str(e)}")
            print(traceback.format_exc())
            return False
    except ImportError:
        print("❌ La biblioteca Transbank no está instalada")
        print("   Instala la biblioteca con: pip install transbank-sdk")
        return False

if __name__ == "__main__":
    success = check_transbank_installation()
    sys.exit(0 if success else 1)