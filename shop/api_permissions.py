from rest_framework import permissions

class IsAdminOrHasAPIAccess(permissions.BasePermission):
    """
    Custom permission to only allow admin users or users with API access.
    """
    
    def has_permission(self, request, view):
        # Allow admin users
        if request.user.is_staff:
            return True
        
        # Check if user has API access (you can customize this logic)
        # For example, you might have a UserProfile model with an has_api_access field
        if hasattr(request.user, 'profile') and getattr(request.user.profile, 'has_api_access', False):
            return True
        
        return False
