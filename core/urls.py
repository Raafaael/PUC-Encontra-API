from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    ConfirmarResetSenhaAPIView,
    DesativarContaAPIView,
    LocalViewSet,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ObjetoViewSet,
    RegistroAPIView,
    SolicitarResetSenhaAPIView,
    TrocaSenhaAPIView,
    UsuarioAdminViewSet,
)

router = DefaultRouter()
router.register("objetos", ObjetoViewSet, basename="objeto")
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("locais", LocalViewSet, basename="local")
router.register("usuarios", UsuarioAdminViewSet, basename="usuario-admin")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegistroAPIView.as_view(), name="auth-register"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/deactivate/", DesativarContaAPIView.as_view(), name="auth-deactivate"),
    path("auth/me/", MeAPIView.as_view(), name="auth-me"),
    path("auth/password/change/", TrocaSenhaAPIView.as_view(), name="auth-password-change"),
    path("auth/password/reset/request/", SolicitarResetSenhaAPIView.as_view(), name="auth-password-reset-request"),
    path("auth/password/reset/confirm/", ConfirmarResetSenhaAPIView.as_view(), name="auth-password-reset-confirm"),
]
