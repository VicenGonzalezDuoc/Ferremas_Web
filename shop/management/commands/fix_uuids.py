from django.core.management.base import BaseCommand
from django.db import connection, transaction
import uuid

class Command(BaseCommand):
    help = 'Corrige UUIDs inválidos en la tabla de productos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando corrección de UUIDs inválidos...'))
        
        # Obtener todos los IDs directamente de la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM shop_product")
            rows = cursor.fetchall()
        
        total_products = len(rows)
        invalid_count = 0
        fixed_count = 0
        
        self.stdout.write(f"Encontrados {total_products} productos en total")
        
        # Verificar cada ID
        for row in rows:
            product_id = row[0]
            try:
                # Intentar convertir a UUID
                uuid.UUID(str(product_id))
            except (ValueError, AttributeError):
                invalid_count += 1
                self.stdout.write(f"ID inválido encontrado: {product_id}")
                
                # Usar una transacción para asegurar la integridad
                with transaction.atomic():
                    # Primero, identificar todas las tablas relacionadas
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name LIKE 'shop_%'
                            """
                        )
                        tables = [table[0] for table in cursor.fetchall()]
                    
                    # Buscar columnas que podrían referenciar a shop_product.id
                    related_tables = []
                    for table in tables:
                        if table == 'shop_product':
                            continue
                        
                        with connection.cursor() as cursor:
                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = cursor.fetchall()
                            
                            for column in columns:
                                column_name = column[1]
                                if column_name.endswith('_id') or column_name == 'product_id':
                                    # Verificar si hay referencias al producto
                                    cursor.execute(
                                        f"SELECT COUNT(*) FROM {table} WHERE {column_name} = %s",
                                        [product_id]
                                    )
                                    count = cursor.fetchone()[0]
                                    if count > 0:
                                        related_tables.append((table, column_name, count))
                    
                    if related_tables:
                        self.stdout.write(self.style.WARNING(f"  - Encontradas {len(related_tables)} tablas relacionadas:"))
                        for table, column, count in related_tables:
                            self.stdout.write(f"    * {table}.{column}: {count} referencias")
                        
                        # Preguntar al usuario si desea continuar
                        self.stdout.write(self.style.WARNING(f"  - ADVERTENCIA: Cambiar el ID afectará a estas relaciones."))
                        self.stdout.write(self.style.WARNING(f"  - Se recomienda hacer una copia de seguridad de la base de datos antes de continuar."))
                        
                        # Generar un nuevo UUID
                        new_id = str(uuid.uuid4())
                        
                        # Actualizar todas las referencias
                        for table, column, _ in related_tables:
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    f"UPDATE {table} SET {column} = %s WHERE {column} = %s",
                                    [new_id, product_id]
                                )
                                self.stdout.write(self.style.SUCCESS(f"    * Actualizadas referencias en {table}.{column}"))
                        
                        # Finalmente, actualizar el producto
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                UPDATE shop_product 
                                SET id = %s 
                                WHERE id = %s
                                """,
                                [new_id, product_id]
                            )
                        
                        fixed_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  - Corregido: {product_id} -> {new_id}"))
                    else:
                        # Si no hay referencias, simplemente actualizar el ID
                        new_id = str(uuid.uuid4())
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                UPDATE shop_product 
                                SET id = %s 
                                WHERE id = %s
                                """,
                                [new_id, product_id]
                            )
                        
                        fixed_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  - Corregido: {product_id} -> {new_id}"))
        
        self.stdout.write("\nResumen:")
        self.stdout.write(f"- Total de productos: {total_products}")
        self.stdout.write(f"- UUIDs inválidos encontrados: {invalid_count}")
        self.stdout.write(f"- UUIDs corregidos: {fixed_count}")
        
        if invalid_count == 0:
            self.stdout.write(self.style.SUCCESS("\n¡No se encontraron UUIDs inválidos!"))
        elif fixed_count == invalid_count:
            self.stdout.write(self.style.SUCCESS("\n¡Todos los UUIDs inválidos han sido corregidos!"))
        else:
            self.stdout.write(self.style.WARNING(f"\nATENCIÓN: No se pudieron corregir todos los UUIDs inválidos ({invalid_count - fixed_count} restantes)"))
