from rest_framework import permissions


def usuario_admin(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return usuario_admin(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return usuario_admin(request.user) or obj.usuario_id == request.user.id
