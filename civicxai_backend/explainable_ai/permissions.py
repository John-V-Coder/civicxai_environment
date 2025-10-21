from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object
        return obj.author == request.user or obj.created_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to create/edit.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to admins
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsContributorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow contributors and admins to create/edit.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to contributors and admins
        return request.user and request.user.is_authenticated and (
            request.user.role in ['contributor', 'admin'] or request.user.is_superuser
        )


class IsAdminOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins full access.
    Non-admins and unauthenticated users are completely denied.
    """
    
    def has_permission(self, request, view):
        # Only admins can access
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )
    
    def has_object_permission(self, request, view, obj):
        # Only admins can access objects
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )
