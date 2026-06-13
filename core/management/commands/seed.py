from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Categoria, Local, Objeto, Perfil


class Command(BaseCommand):
    help = "Cria dados iniciais para apresentacao e testes locais."

    def handle(self, *args, **options):
        User = get_user_model()
        senha = "PucEncontra123"

        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@puc-encontra.local", "first_name": "Admin"},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(senha)
        admin.save()
        Perfil.objects.update_or_create(user=admin, defaults={"tipo": Perfil.TIPO_ADMIN})

        aluno1, _ = User.objects.get_or_create(
            username="aluno1",
            defaults={"email": "aluno1@puc-encontra.local", "first_name": "Ana"},
        )
        aluno1.set_password(senha)
        aluno1.save()
        Perfil.objects.update_or_create(
            user=aluno1,
            defaults={"matricula": "20260001", "telefone": "(21) 99999-0001"},
        )

        aluno2, _ = User.objects.get_or_create(
            username="aluno2",
            defaults={"email": "aluno2@puc-encontra.local", "first_name": "Bruno"},
        )
        aluno2.set_password(senha)
        aluno2.save()
        Perfil.objects.update_or_create(
            user=aluno2,
            defaults={"matricula": "20260002", "telefone": "(21) 99999-0002"},
        )

        categorias = {
            "Documento": "Carteiras, crachas, identidades e cartoes.",
            "Eletronico": "Celulares, notebooks, carregadores e fones.",
            "Material de estudo": "Livros, cadernos, estojos e apostilas.",
            "Acessorio": "Chaves, garrafas, oculos e itens pessoais.",
        }
        categoria_objs = {
            nome: Categoria.objects.get_or_create(nome=nome, defaults={"descricao": descricao})[0]
            for nome, descricao in categorias.items()
        }

        locais = [
            ("Biblioteca Central", "Edificio Frings", "2o andar"),
            ("Pilotis", "Campus Gavea", "Terreo"),
            ("Laboratorio de Informatica", "Edificio Cardeal Leme", "3o andar"),
            ("Restaurante Universitario", "Campus Gavea", "Terreo"),
        ]
        local_objs = {
            nome: Local.objects.get_or_create(
                nome=nome,
                predio=predio,
                defaults={"andar": andar, "descricao": f"Area de referencia: {nome}."},
            )[0]
            for nome, predio, andar in locais
        }

        if not Objeto.objects.exists():
            hoje = date.today()
            Objeto.objects.create(
                usuario=aluno1,
                tipo=Objeto.TIPO_PERDIDO,
                titulo="Garrafa azul com adesivo da PUC",
                descricao="Garrafa de aluminio azul esquecida depois da aula de programacao.",
                categoria=categoria_objs["Acessorio"],
                local=local_objs["Laboratorio de Informatica"],
                data_ocorrencia=hoje - timedelta(days=1),
                ponto_referencia="Bancada perto da janela",
                contato="aluno1@puc-encontra.local",
                imagem_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80",
            )
            Objeto.objects.create(
                usuario=aluno2,
                tipo=Objeto.TIPO_ENCONTRADO,
                titulo="Carteira preta",
                descricao="Carteira encontrada no Pilotis com cartoes no interior.",
                categoria=categoria_objs["Documento"],
                local=local_objs["Pilotis"],
                data_ocorrencia=hoje - timedelta(days=2),
                ponto_referencia="Proximo aos bancos centrais",
                contato="Seguranca do campus",
                imagem_url="https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80",
            )
            Objeto.objects.create(
                usuario=aluno1,
                tipo=Objeto.TIPO_ENCONTRADO,
                status=Objeto.STATUS_RESOLVIDO,
                titulo="Carregador USB-C",
                descricao="Carregador devolvido ao dono apos contato pelo sistema.",
                categoria=categoria_objs["Eletronico"],
                local=local_objs["Biblioteca Central"],
                data_ocorrencia=hoje - timedelta(days=5),
                ponto_referencia="Mesa coletiva",
                contato="aluno1@puc-encontra.local",
            )

        self.stdout.write(self.style.SUCCESS("Dados iniciais criados/atualizados."))
