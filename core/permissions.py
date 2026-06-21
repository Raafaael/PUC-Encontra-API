from rest_framework import permissions


def usuario_admin(user):
    # Centraliza a regra de administrador usada por permississoes e filtros de consulta.
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Visitantes podem consultar cadastros auxiliares; alteracoes ficam restritas ao admin.
        if request.method in permissions.SAFE_METHODS:
            return True
        return usuario_admin(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # A leitura publica preserva a vitrine; edicao/exclusao fica com dono do registro ou admin.
        if request.method in permissions.SAFE_METHODS:
            return True
        return usuario_admin(request.user) or obj.usuario_id == request.user.id
