from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Categoria, Local, Objeto, Perfil

User = get_user_model()


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ["tipo", "matricula", "telefone"]
        read_only_fields = ["tipo"]


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)
    nome = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "nome", "perfil", "is_staff"]
        read_only_fields = ["id", "is_staff"]

    def get_nome(self, obj) -> str:
        return obj.get_full_name() or obj.username


class AdminUsuarioSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)
    nome = serializers.SerializerMethodField()
    matricula = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telefone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tipo = serializers.ChoiceField(choices=Perfil.TIPO_CHOICES, write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "nome",
            "perfil",
            "is_staff",
            "is_active",
            "matricula",
            "telefone",
            "tipo",
            "password",
            "password_confirm",
        ]
        read_only_fields = ["id", "nome", "perfil"]

    def get_nome(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def validate_username(self, value):
        queryset = User.objects.filter(username__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Este nome de usuario ja esta em uso.")
        return value

    def validate_email(self, value):
        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Este e-mail ja esta em uso.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if self.instance is None and not password:
            raise serializers.ValidationError({"password": "Informe uma senha."})
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({"password_confirm": "As senhas nao conferem."})
            user = self.instance or User(username=attrs.get("username"), email=attrs.get("email"))
            password_validation.validate_password(password, user)

        return attrs

    def _save_perfil(self, user, attrs):
        tipo = attrs.pop("tipo", None)
        matricula = attrs.pop("matricula", None)
        telefone = attrs.pop("telefone", None)

        perfil_defaults = {}
        if tipo is not None:
            perfil_defaults["tipo"] = tipo
            user.is_staff = tipo == Perfil.TIPO_ADMIN
            user.save(update_fields=["is_staff"])
        if matricula is not None:
            perfil_defaults["matricula"] = matricula
        if telefone is not None:
            perfil_defaults["telefone"] = telefone

        if perfil_defaults:
            Perfil.objects.update_or_create(user=user, defaults=perfil_defaults)

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm", None)
        perfil_data = {
            "tipo": validated_data.pop("tipo", Perfil.TIPO_ADMIN if validated_data.get("is_staff", True) else Perfil.TIPO_USUARIO),
            "matricula": validated_data.pop("matricula", ""),
            "telefone": validated_data.pop("telefone", ""),
        }
        user = User.objects.create_user(**validated_data, password=password)
        self._save_perfil(user, perfil_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("password_confirm", None)
        perfil_data = {
            key: validated_data.pop(key)
            for key in ["tipo", "matricula", "telefone"]
            if key in validated_data
        }

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        self._save_perfil(instance, perfil_data)
        return instance


class MensagemSerializer(serializers.Serializer):
    detail = serializers.CharField()


class RegistroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=20, required=False, allow_blank=True)
    telefone = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este nome de usuario ja esta em uso.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este e-mail ja esta em uso.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "As senhas nao conferem."})
        user = User(username=attrs["username"], email=attrs["email"])
        password_validation.validate_password(attrs["password"], user)
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        matricula = validated_data.pop("matricula", "")
        telefone = validated_data.pop("telefone", "")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        Perfil.objects.update_or_create(
            user=user,
            defaults={"matricula": matricula, "telefone": telefone},
        )
        return user


class LoginSerializer(serializers.Serializer):
    identificador = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identificador = attrs["identificador"]
        username = identificador
        if "@" in identificador:
            user = User.objects.filter(email__iexact=identificador).first()
            if user:
                username = user.username

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Usuario/e-mail ou senha invalidos.")
        if not user.is_active:
            raise serializers.ValidationError("Esta conta esta desativada.")
        attrs["user"] = user
        return attrs


class AuthRespostaSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UsuarioSerializer()

    @staticmethod
    def build(user):
        token, _ = Token.objects.get_or_create(user=user)
        return {"token": token.key, "user": UsuarioSerializer(user).data}


class PerfilUpdateSerializer(serializers.ModelSerializer):
    matricula = serializers.CharField(source="perfil.matricula", required=False, allow_blank=True)
    telefone = serializers.CharField(source="perfil.telefone", required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "matricula", "telefone"]

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop("perfil", {})
        instance = super().update(instance, validated_data)
        if perfil_data:
            Perfil.objects.update_or_create(user=instance, defaults=perfil_data)
        return instance


class TrocaSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True, min_length=8)

    def validate_senha_atual(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate_nova_senha(self, value):
        password_validation.validate_password(value, self.context["request"].user)
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["nova_senha"])
        user.save(update_fields=["password"])
        return user


class SolicitarResetSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        user = User.objects.filter(email__iexact=self.validated_data["email"], is_active=True).first()
        if not user:
            return {"detail": "Se o e-mail existir, enviaremos instrucoes de recuperacao."}

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = {"detail": "Se o e-mail existir, enviaremos instrucoes de recuperacao."}
        if settings.PASSWORD_RESET_EXPOSE_TOKEN:
            response["reset"] = {"uid": uid, "token": token}
        return response


class ConfirmarResetSenhaSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    nova_senha = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Link de recuperacao invalido.")

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Token de recuperacao invalido ou expirado.")
        password_validation.validate_password(attrs["nova_senha"], user)
        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["nova_senha"])
        user.save(update_fields=["password"])
        Token.objects.filter(user=user).delete()
        return user


class CategoriaSerializer(serializers.ModelSerializer):
    objetos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nome", "descricao", "objetos_count"]


class LocalSerializer(serializers.ModelSerializer):
    objetos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Local
        fields = ["id", "nome", "predio", "andar", "descricao", "objetos_count"]


class ObjetoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)
    local_nome = serializers.CharField(source="local.nome", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    imagem_exibicao = serializers.SerializerMethodField()

    class Meta:
        model = Objeto
        fields = [
            "id",
            "usuario",
            "tipo",
            "tipo_display",
            "status",
            "status_display",
            "titulo",
            "descricao",
            "categoria",
            "categoria_nome",
            "local",
            "local_nome",
            "data_ocorrencia",
            "ponto_referencia",
            "contato",
            "imagem",
            "imagem_url",
            "imagem_exibicao",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "usuario", "imagem_exibicao", "criado_em", "atualizado_em"]

    def get_imagem_exibicao(self, obj):
        # O frontend roda em outra porta, entao uploads locais precisam voltar como URL absoluta.
        if obj.imagem:
            request = self.context.get("request")
            url = obj.imagem.url
            return request.build_absolute_uri(url) if request else url
        return obj.imagem_url
