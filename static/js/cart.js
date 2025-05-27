document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los botones de añadir al carrito
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    // Añadir evento click a cada botón
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const url = this.getAttribute('href');
            
            // Mostrar indicador de carga
            this.innerHTML = '<i class="bi bi-hourglass-split"></i> Añadiendo...';
            this.disabled = true;
            
            // Realizar solicitud AJAX
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar contador del carrito en el navbar
                    const cartCounter = document.querySelector('.cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_count;
                        cartCounter.classList.remove('d-none');
                    }
                    
                    // Mostrar mensaje de éxito
                    showNotification('success', `${productName} añadido al carrito.`);
                } else {
                    showNotification('danger', data.message || 'Error al añadir al carrito.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('danger', 'Error al añadir al carrito. Inténtelo de nuevo.');
            })
            .finally(() => {
                // Restaurar botón
                this.innerHTML = '<i class="bi bi-cart-plus"></i> Añadir';
                this.disabled = false;
            });
        });
    });
    
    // Actualizar carrito con AJAX
    // Manejar formularios de actualización de carrito
    const updateForms = document.querySelectorAll('.update-cart-form');
    
    updateForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.getAttribute('action');
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar subtotal del item
                    const itemRow = this.closest('tr');
                    const subtotalCell = itemRow.querySelector('.item-subtotal');
                    if (subtotalCell) {
                        subtotalCell.textContent = `$${data.item_subtotal.toFixed(2)}`;
                    }
                    
                    // Actualizar total del carrito
                    const cartTotal = document.querySelector('.cart-total');
                    if (cartTotal) {
                        cartTotal.textContent = `$${data.cart_total.toFixed(2)}`;
                    }
                    
                    // Actualizar contador del carrito
                    const cartCounter = document.querySelector('.cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_count;
                    }
                    
                    // Mostrar mensaje
                    showNotification('success', data.message);
                } else {
                    showNotification('danger', data.message || 'Error al actualizar el carrito');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('danger', 'Error al actualizar el carrito');
            });
        });
    });
    
    // Manejar enlaces de eliminar del carrito
    const removeLinks = document.querySelectorAll('.remove-from-cart');
    
    removeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const itemId = this.dataset.itemId;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Eliminar fila del item
                    const itemRow = document.getElementById(`cart-item-${itemId}`);
                    if (itemRow) {
                        itemRow.remove();
                    }
                    
                    // Actualizar total del carrito
                    const cartTotal = document.querySelector('.cart-total');
                    if (cartTotal) {
                        cartTotal.textContent = `$${data.cart_total.toFixed(2)}`;
                    }
                    
                    // Actualizar contador del carrito
                    const cartCounter = document.querySelector('.cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_count;
                    }
                    
                    // Mostrar mensaje
                    showNotification('success', data.message);
                    
                    // Si el carrito está vacío, recargar la página
                    if (data.cart_count === 0) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    showNotification('danger', data.message || 'Error al eliminar el producto');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('danger', 'Error al eliminar el producto');
            });
        });
    });
    
    // Función para mostrar notificaciones
    function showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = message;
        document.body.appendChild(notification);
        
        // Mostrar notificación
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
});
