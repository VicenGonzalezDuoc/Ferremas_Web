"""
Script para verificar la instalación de la biblioteca Transbank
"""
import sys
import importlib.util
import importlib
import pkgutil
import inspect
import traceback

def check_module(module_name):
    """Verifica si un módulo está instalado y puede ser importado"""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ El módulo {module_name} NO está instalado")
        return False
    else:
        print(f"✅ El módulo {module_name} está instalado")
        return True

def list_submodules(package_name):
    """Lista todos los submódulos de un paquete"""
    try:
        package = importlib.import_module(package_name)
        print(f"\nSubmódulos de {package_name}:")
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
            print(f"  - {name}")
    except ImportError:
        print(f"No se pudo importar el paquete {package_name}")

def explore_module(module_name):
    """Explora un módulo y muestra sus clases y funciones"""
    try:
        module = importlib.import_module(module_name)
        print(f"\nContenido del módulo {module_name}:")
        
        # Listar clases y funciones
        for name, obj in inspect.getmembers(module):
            if not name.startswith('_'):  # Ignorar miembros privados
                obj_type = type(obj).__name__
                print(f"  - {name} ({obj_type})")
                
                # Si es una clase, mostrar sus métodos y su jerarquía
                if obj_type == 'type':
                    print(f"    Métodos de {name}:")
                    for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                        if not method_name.startswith('_'):
                            try:
                                print(f"      - {method_name}{inspect.signature(method)}")
                            except ValueError:
                                print(f"      - {method_name}()")
                    
                    # Mostrar la jerarquía de clases
                    print(f"    Hereda de: {', '.join([base.__name__ for base in obj.__bases__])}")
    except ImportError:
        print(f"No se pudo importar el módulo {module_name}")

def find_concrete_options_classes():
    """Busca clases concretas que implementen Options"""
    try:
        from transbank.common.options import Options
        
        # Buscar en todos los submódulos de transbank
        concrete_options = []
        
        def search_in_module(module_name):
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    # Verificar si es una clase que hereda de Options pero no es Options
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Options) and 
                        obj != Options and 
                        not inspect.isabstract(obj)):
                        concrete_options.append((name, obj, module_name))
                
                # Buscar en submódulos
                try:
                    for _, submodule_name, is_pkg in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
                        search_in_module(submodule_name)
                except (AttributeError, ImportError):
                    pass  # El módulo no tiene submódulos
            except ImportError:
                pass  # No se pudo importar el módulo
        
        # Comenzar la búsqueda desde el módulo raíz
        search_in_module('transbank')
        
        return concrete_options
    except ImportError:
        print("No se pudo importar Options de transbank.common.options")
        return []

def check_transbank():
    """Verifica la instalación de la biblioteca Transbank"""
    print("Verificando la instalación de Transbank...")
    
    # Verificar el módulo principal
    if not check_module("transbank"):
        print("\nLa biblioteca Transbank no está instalada.")
        print("Por favor, instálala con: pip install transbank-sdk")
        return False
    
    # Obtener la versión de Transbank
    try:
        import transbank
        version = getattr(transbank, "__version__", "Desconocida")
        print(f"\nVersión de Transbank: {version}")
    except ImportError:
        print("\nNo se pudo determinar la versión de Transbank")
    
    # Listar submódulos para diagnóstico
    list_submodules("transbank")
    list_submodules("transbank.webpay")
    list_submodules("transbank.common")
    
    # Explorar módulos específicos para encontrar las clases de opciones
    try:
        explore_module("transbank.common.options")
    except:
        print("No se pudo explorar transbank.common.options")
    
    try:
        explore_module("transbank.webpay.webpay_plus")
    except:
        print("No se pudo explorar transbank.webpay.webpay_plus")
    
    # Para la versión 6.0.0, verificar los módulos correctos
    modules_to_check = [
        "transbank.webpay",
        "transbank.common"
    ]
    
    all_ok = True
    for module in modules_to_check:
        if not check_module(module):
            all_ok = False
    
    if all_ok:
        print("\nLos módulos básicos de Transbank están instalados.")
        
        # Intentar importar y usar las clases para la versión 6.0.0
        try:
            from transbank.webpay.webpay_plus.transaction import Transaction
            print("✅ Se pudo importar Transaction")
            
            # Intentar encontrar la clase de opciones correcta
            try:
                # Primero, intentar importar IntegrationType
                from transbank.common.integration_type import IntegrationType
                print("✅ Se pudo importar IntegrationType")
                
                # Buscar clases concretas que implementen Options
                concrete_options = find_concrete_options_classes()
                
                if concrete_options:
                    print("\nClases concretas que implementan Options:")
                    for name, cls, module in concrete_options:
                        print(f"  - {name} (en {module})")
                    
                    # Intentar usar la clase WebpayOptions del módulo webpay_plus.transaction
                    target_module = "transbank.webpay.webpay_plus.transaction"
                    target_options = None
                    
                    for name, options_class, module in concrete_options:
                        if module == target_module and name == "WebpayOptions":
                            target_options = (name, options_class, module)
                            break
                    
                    # Si no encontramos la clase específica, usar la primera WebpayOptions
                    if not target_options:
                        for name, options_class, module in concrete_options:
                            if name == "WebpayOptions":
                                target_options = (name, options_class, module)
                                break
                    
                    # Si aún no encontramos, usar la primera opción
                    if not target_options and concrete_options:
                        target_options = concrete_options[0]
                    
                    if target_options:
                        name, options_class, module = target_options
                        try:
                            print(f"\nProbando con {name} de {module}...")
                            options = options_class("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C", IntegrationType.TEST)
                            tx = Transaction(options)
                            print(f"✅ Se pudo crear una instancia de Transaction con {name}")
                            
                            # Probar crear una transacción
                            try:
                                response = tx.create("OC123456", "S123", 1000, "http://localhost:8000/webpay/return")
                                print(f"✅ Se pudo crear una transacción de prueba")
                                
                                # Verificar si la respuesta es un diccionario
                                if isinstance(response, dict):
                                    print(f"La respuesta es un diccionario con claves: {', '.join(response.keys())}")
                                    if 'token' in response and 'url' in response:
                                        print(f"Token: {response['token']}")
                                        print(f"URL: {response['url']}")
                                        return True
                                    else:
                                        print(f"El diccionario no contiene las claves esperadas. Contenido: {response}")
                                else:
                                    # Intentar acceder a los atributos
                                    try:
                                        print(f"Token: {response.token}")
                                        print(f"URL: {response.url}")
                                        return True
                                    except AttributeError:
                                        print(f"La respuesta no tiene los atributos esperados. Tipo: {type(response)}")
                                        print(f"Contenido: {response}")
                            except Exception as e:
                                print(f"❌ Error al crear una transacción de prueba con {name}: {str(e)}")
                                print(traceback.format_exc())
                        except Exception as e:
                            print(f"❌ Error al crear una instancia de Transaction con {name}: {str(e)}")
                            print(traceback.format_exc())
                    else:
                        print("❌ No se encontró ninguna clase de opciones adecuada")
                else:
                    print("❌ No se encontraron clases concretas que implementen Options")
                    
                    # Intentar crear una clase concreta que implemente Options
                    try:
                        from transbank.common.options import Options
                        
                        print("\nCreando una implementación personalizada de Options...")
                        
                        class CustomOptions(Options):
                            def __init__(self, commerce_code, api_key, integration_type):
                                super().__init__(commerce_code, api_key, integration_type)
                            
                            @property
                            def header_commerce_code_name(self):
                                return "Tbk-Api-Key-Id"
                            
                            @property
                            def header_api_key_name(self):
                                return "Tbk-Api-Key"
                        
                        # Probar con la implementación personalizada
                        try:
                            options = CustomOptions("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C", IntegrationType.TEST)
                            tx = Transaction(options)
                            print("✅ Se pudo crear una instancia de Transaction con CustomOptions")
                            
                            # Probar crear una transacción
                            try:
                                response = tx.create("OC123456", "S123", 1000, "http://localhost:8000/webpay/return")
                                print(f"✅ Se pudo crear una transacción de prueba")
                                
                                # Verificar si la respuesta es un diccionario
                                if isinstance(response, dict):
                                    print(f"La respuesta es un diccionario con claves: {', '.join(response.keys())}")
                                    if 'token' in response and 'url' in response:
                                        print(f"Token: {response['token']}")
                                        print(f"URL: {response['url']}")
                                        return True
                                    else:
                                        print(f"El diccionario no contiene las claves esperadas. Contenido: {response}")
                                else:
                                    # Intentar acceder a los atributos
                                    try:
                                        print(f"Token: {response.token}")
                                        print(f"URL: {response.url}")
                                        return True
                                    except AttributeError:
                                        print(f"La respuesta no tiene los atributos esperados. Tipo: {type(response)}")
                                        print(f"Contenido: {response}")
                            except Exception as e:
                                print(f"❌ Error al crear una transacción de prueba con CustomOptions: {str(e)}")
                                print(traceback.format_exc())
                        except Exception as e:
                            print(f"❌ Error al crear una instancia de Transaction con CustomOptions: {str(e)}")
                            print(traceback.format_exc())
                    except Exception as e:
                        print(f"❌ Error al crear una implementación personalizada de Options: {str(e)}")
                        print(traceback.format_exc())
            except Exception as e:
                print(f"❌ Error al buscar la clase de opciones: {str(e)}")
                print(traceback.format_exc())
            
            # Si llegamos aquí, no se pudo crear una instancia de Transaction
            print("❌ No se pudo crear una instancia de Transaction")
            return False
        except Exception as e:
            print(f"❌ Error al importar las clases de Transbank v6.0.0: {str(e)}")
            print(traceback.format_exc())
            return False
    else:
        print("\nAlgunos módulos de Transbank no están instalados correctamente.")
        print("Por favor, reinstala la biblioteca con: pip install transbank-sdk==6.0.0")
        return False

if __name__ == "__main__":
    success = check_transbank()
    sys.exit(0 if success else 1)

