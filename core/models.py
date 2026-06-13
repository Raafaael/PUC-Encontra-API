from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    TIPO_USUARIO = "usuario"
    TIPO_ADMIN = "admin"

    TIPO_CHOICES = [
        (TIPO_USUARIO, "Usuario"),
        (TIPO_ADMIN, "Administrador"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default=TIPO_USUARIO)
    matricula = models.CharField(max_length=20, blank=True)
    telefone = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        constraints = [
            models.UniqueConstraint(
                fields=["matricula"],
                condition=~models.Q(matricula=""),
                name="unique_perfil_matricula_not_blank",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Local(models.Model):
    nome = models.CharField(max_length=150)
    predio = models.CharField(max_length=100)
    andar = models.CharField(max_length=30, blank=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["predio", "nome"]
        unique_together = ["nome", "predio"]
        verbose_name = "Local"
        verbose_name_plural = "Locais"

    def __str__(self):
        partes = [self.nome, self.predio]
        if self.andar:
            partes.append(self.andar)
        return " - ".join(partes)


class Objeto(models.Model):
    TIPO_PERDIDO = "perdido"
    TIPO_ENCONTRADO = "encontrado"

    STATUS_PENDENTE = "pendente"
    STATUS_ATIVO = "ativo"
    STATUS_RESOLVIDO = "resolvido"

    TIPO_CHOICES = [
        (TIPO_PERDIDO, "Perdido"),
        (TIPO_ENCONTRADO, "Encontrado"),
    ]
    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_ATIVO, "Ativo"),
        (STATUS_RESOLVIDO, "Resolvido"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="objetos")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ATIVO)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="objetos",
    )
    local = models.ForeignKey(
        Local,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="objetos",
    )
    data_ocorrencia = models.DateField()
    ponto_referencia = models.CharField(max_length=200, blank=True)
    contato = models.CharField(max_length=120, blank=True)
    imagem_url = models.URLField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Objeto"
        verbose_name_plural = "Objetos"

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"
