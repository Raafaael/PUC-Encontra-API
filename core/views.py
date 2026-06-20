from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Categoria, Local, Objeto
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, usuario_admin
from .serializers import (
    AuthRespostaSerializer,
    AdminUsuarioSerializer,
    CategoriaSerializer,
    ConfirmarResetSenhaSerializer,
    LocalSerializer,
    LoginSerializer,
    MensagemSerializer,
    ObjetoSerializer,
    PerfilUpdateSerializer,
    RegistroSerializer,
    SolicitarResetSenhaSerializer,
    TrocaSenhaSerializer,
    UsuarioSerializer,
)

User = get_user_model()


class RegistroAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer

    @extend_schema(request=RegistroSerializer, responses={201: AuthRespostaSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AuthRespostaSerializer.build(user), status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer, responses={200: AuthRespostaSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(AuthRespostaSerializer.build(serializer.validated_data["user"]))


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MensagemSerializer

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UsuarioSerializer

    @extend_schema(responses={200: UsuarioSerializer})
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)

    @extend_schema(request=PerfilUpdateSerializer, responses={200: UsuarioSerializer})
    def patch(self, request):
        serializer = PerfilUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UsuarioSerializer(request.user).data)


class TrocaSenhaAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TrocaSenhaSerializer

    @extend_schema(request=TrocaSenhaSerializer, responses={200: MensagemSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."})


class DesativarContaAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MensagemSerializer

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        Token.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SolicitarResetSenhaAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SolicitarResetSenhaSerializer

    @extend_schema(request=SolicitarResetSenhaSerializer, responses={200: MensagemSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class ConfirmarResetSenhaAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmarResetSenhaSerializer

    @extend_schema(request=ConfirmarResetSenhaSerializer, responses={200: MensagemSerializer})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha redefinida com sucesso."})


class UsuarioAdminViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUsuarioSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.select_related("perfil").order_by("first_name", "username")


@extend_schema_view(
    list=extend_schema(parameters=[OpenApiParameter("search", str), OpenApiParameter("tipo", str)]),
)
class ObjetoViewSet(viewsets.ModelViewSet):
    serializer_class = ObjetoSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Objeto.objects.select_related("usuario", "usuario__perfil", "categoria", "local")
            .all()
        )

        if usuario_admin(user):
            pass
        elif user.is_authenticated:
            queryset = queryset.filter(Q(status=Objeto.STATUS_ATIVO) | Q(usuario=user))
        else:
            queryset = queryset.filter(status=Objeto.STATUS_ATIVO)

        if self.request.query_params.get("meus") in {"1", "true", "sim"}:
            queryset = queryset.filter(usuario=user) if user.is_authenticated else queryset.none()

        tipo = self.request.query_params.get("tipo")
        status_param = self.request.query_params.get("status")
        categoria = self.request.query_params.get("categoria")
        local = self.request.query_params.get("local")
        search = self.request.query_params.get("search")

        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if local:
            queryset = queryset.filter(local_id=local)
        if search:
            queryset = queryset.filter(Q(titulo__icontains=search) | Q(descricao__icontains=search))

        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def meus(self, request):
        queryset = self.filter_queryset(self.get_queryset().filter(usuario=request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def marcar_resolvido(self, request, pk=None):
        objeto = self.get_object()
        objeto.status = Objeto.STATUS_RESOLVIDO
        objeto.save(update_fields=["status", "atualizado_em"])
        return Response(self.get_serializer(objeto).data)


class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Categoria.objects.annotate(objetos_count=Count("objetos")).order_by("nome")


class LocalViewSet(viewsets.ModelViewSet):
    serializer_class = LocalSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Local.objects.annotate(objetos_count=Count("objetos")).order_by("predio", "nome")
