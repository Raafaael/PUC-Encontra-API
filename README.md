# Segundo Trabalho de Programacao para Web - PUC-Encontra API

Backend do PUC-Encontra, uma plataforma de achados e perdidos para o ambiente da PUC. Esta API concentra regras de negocio, autenticacao, permissoes, CRUD de objetos, categorias, locais, usuarios administrativos, upload de imagens e documentacao Swagger.

## Integrantes

- Dante Navaza
- Rafael Soares

## Links

- Repositorio do backend: [https://github.com/Raafaael/PUC-Encontra-API](https://github.com/Raafaael/PUC-Encontra-API)
- Repositorio do frontend: [https://github.com/Raafaael/PUC-Encontra-FrontEnd](https://github.com/Raafaael/PUC-Encontra-FrontEnd)
- API local: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- Swagger local: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- Site backend publicado: pendente de publicacao em provedor web

## Escopo

O backend foi desenvolvido em Django e Django REST Framework, sem HTML, CSS ou JavaScript proprios. Ele atende ao frontend com uma API REST para:

- Cadastro, login, logout e consulta do usuario autenticado.
- Troca de senha e fluxo de recuperacao de senha.
- Desativacao de conta.
- CRUD de objetos perdidos e encontrados.
- CRUD administrativo de categorias.
- CRUD administrativo de locais.
- CRUD administrativo de usuarios.
- Upload de imagem local para objetos.
- Consulta publica de itens ativos.
- Area privada para "Meus Registros".
- Fluxo administrativo para aprovar, rejeitar e resolver objetos.
- Documentacao e testes manuais via Swagger.

## Tecnologias

- Python 3
- Django 5
- Django REST Framework
- drf-spectacular
- django-cors-headers
- SQLite em desenvolvimento
- Token Authentication
- Pillow para validacao de imagens
- WhiteNoise para arquivos estaticos em ambientes de deploy

## Instalacao Local

Clone o repositorio e entre na pasta:

```bash
git clone https://github.com/Raafaael/PUC-Encontra-API.git
cd PUC-Encontra-API
```

Crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Opcionalmente crie o arquivo `.env` com base no exemplo:

```bash
cp .env.example .env
```

Aplique as migracoes:

```bash
python manage.py migrate
```

Crie os dados iniciais para apresentacao:

```bash
python manage.py seed
```

Execute o backend localmente:

```bash
SERVE_MEDIA=True python manage.py runserver 127.0.0.1:8000
```

O parametro `SERVE_MEDIA=True` permite abrir imagens enviadas para `/media/...` durante a demonstracao local.

## Usuarios de Teste

Todos os usuarios criados pelo seed usam a senha:

```text
PucEncontra123
```

Usuarios:

```text
admin   - Administrador - admin@puc-encontra.local
aluno1  - Usuario comum - aluno1@puc-encontra.local
aluno2  - Usuario comum - aluno2@puc-encontra.local
```

## Manual de Uso da API

1. Acesse o Swagger em [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/).
2. Faca login em `POST /api/auth/login/` com `identificador` e `password`.
3. Copie o token retornado.
4. Clique em `Authorize` no Swagger.
5. Informe o token no formato:

```text
Token seu_token_aqui
```

Depois da autenticacao, os endpoints protegidos podem ser testados diretamente pelo Swagger.

## Endpoints Principais

Autenticacao:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
PATCH /api/auth/me/
POST /api/auth/password/change/
POST /api/auth/password/reset/request/
POST /api/auth/password/reset/confirm/
POST /api/auth/deactivate/
```

Objetos:

```text
GET    /api/objetos/
POST   /api/objetos/
GET    /api/objetos/{id}/
PATCH  /api/objetos/{id}/
DELETE /api/objetos/{id}/
GET    /api/objetos/meus/
POST   /api/objetos/{id}/marcar_resolvido/
```

Administracao:

```text
GET/POST/PATCH/DELETE /api/categorias/
GET/POST/PATCH/DELETE /api/locais/
GET/POST/PATCH/DELETE /api/usuarios/
```

## Regras de Acesso

- Visitantes podem consultar itens publicos ativos.
- Usuarios autenticados podem criar objetos e consultar seus proprios registros.
- Usuarios comuns veem seus objetos pendentes e os itens ativos da vitrine publica.
- Administradores veem toda a fila de objetos, incluindo pendentes e resolvidos.
- Apenas administradores alteram categorias, locais e usuarios.
- Apenas o dono do objeto ou um administrador pode editar ou excluir um objeto.

## Imagens

Swagger da API:

![1782080377361](image/README/1782080377361.png)

Exemplo de endpoint na documentacao

![1782080351584](image/README/1782080351584.png)

Exemplo redoc

![1782080600086](image/README/1782080600086.png)

### O Que Foi Testado e Funcionou

Testado localmente em 21/06/2026:

- `python manage.py check` sem erros.
- Migracoes aplicadas com sucesso.
- Seed executado com sucesso.
- Swagger UI abre em `/api/docs/`.
- Schema OpenAPI abre em `/api/schema/`.
- API raiz abre em `/api/`.
- CRUD de categorias testado com create, read, update e delete.
- Endpoint protegido `/api/objetos/meus/` retorna `401` sem token.
- Usuario admin acessa `/api/usuarios/`.
- Usuario comum recebe `403` em `/api/usuarios/`.
- Upload de imagem para objeto funciona.
- URL de imagem em `/media/...` abre localmente com `200 image/png`.

## O Que Nao Funcionou ou Esta Pendente

- Publicacao em provedor web ainda nao foi realizada.
- O envio real de e-mail para recuperacao de senha nao foi configurado; em desenvolvimento, o token de reset aparece na resposta para facilitar a demonstracao.
- O armazenamento de imagens em producao ainda precisa ser configurado em um storage persistente do provedor escolhido.
- Ainda nao ha testes automatizados; os testes feitos foram manuais via curl, navegador e Swagger.

## Comandos de Validacao

```bash
SERVE_MEDIA=True python manage.py check
curl http://127.0.0.1:8000/api/
curl http://127.0.0.1:8000/api/schema/
curl http://127.0.0.1:8000/api/docs/
```

## Observacoes Para Entrega

Para atender integralmente ao PDF, antes do envio no EaD ainda e necessario publicar o backend em um provedor web e substituir o item "Site backend publicado" pelo link final.
