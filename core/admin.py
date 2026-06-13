from django.contrib import admin

from .models import Categoria, Local, Objeto, Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "tipo", "matricula", "telefone")
    search_fields = ("user__username", "user__email", "matricula", "telefone")
    list_filter = ("tipo",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ("nome", "predio", "andar")
    search_fields = ("nome", "predio", "andar")
    list_filter = ("predio",)


@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "status", "usuario", "categoria", "local", "data_ocorrencia")
    list_filter = ("tipo", "status", "categoria", "local")
    search_fields = ("titulo", "descricao", "usuario__username", "usuario__email")
    date_hierarchy = "data_ocorrencia"
