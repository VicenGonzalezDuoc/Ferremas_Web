from rest_framework import permissions

class IsAdminOrHasAPIAccess(permissions.BasePermission):
    """
    Custom permission to only allow admin users or users with API access.
    """
    def has_permission(self, request, view):
        # Check if user is admin
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Add your custom API access logic here
        # For example, check for a specific user attribute or group
        # return request.user.has_api_access
        
        # For now, just allow authenticated users
        return request.user.is_authenticated

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite acceso de lectura a todos los usuarios autenticados,
    pero solo permite escritura a usuarios staff.
    """
    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return False
            
        # Permitir GET, HEAD, OPTIONS a usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permitir escritura solo a usuarios staff
        return request.user.is_staff


