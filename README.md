# Segundo Trabalho de Programacao para Web - PUC-Encontra API

Backend do PUC-Encontra, uma plataforma de achados e perdidos para o ambiente da PUC. Esta API concentra regras de negocio, autenticacao, permissoes, CRUD de objetos, categorias, locais, usuarios administrativos, upload de imagens e documentacao Swagger.

## Integrantes

- Dante Navaza - 2321406
- Rafael Soares - 2320470

## Links

- Site backend publicado: [https://puc-encontra-api.vercel.app/](https://puc-encontra-api.vercel.app/)
- Site frontend publicado: [https://puc-encontra-frontend.vercel.app/](https://puc-encontra-frontend.vercel.app/)

## Escopo

O backend foi desenvolvido em Django e Django REST Framework, sem HTML, CSS ou JavaScript proprios. Ele atende ao frontend com uma API REST para:

- Cadastro, login, logout e consulta do usuario autenticado.
- Troca de senha e fluxo de recuperacao de senha.
- Desativacao de conta.
- Envio de e-mail para recuperacao de senha via SMTP configuravel.
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
- Cloudinary para armazenamento persistente de imagens em producao
- PostgreSQL em producao

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

## Publicacao na Vercel

O repositorio ja contem os arquivos necessarios para deploy na Vercel:

- `api/index.py`: entrypoint WSGI usado pela Vercel.
- `vercel.json`: build de arquivos estaticos e roteamento para a API Django.
- `.python-version`: fixa Python 3.12.

Crie um projeto separado na Vercel apontando para este repositorio e configure as variaveis:

```env
SECRET_KEY=coloque-uma-chave-grande-e-secreta
DEBUG=False
DATABASE_URL=postgres://usuario:senha@host:porta/banco?sslmode=require
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
ALLOWED_HOSTS=SEU-BACKEND.vercel.app
CORS_ALLOWED_ORIGINS=https://SEU-FRONTEND.vercel.app
CSRF_TRUSTED_ORIGINS=https://SEU-BACKEND.vercel.app
SERVE_MEDIA=False
PASSWORD_RESET_EXPOSE_TOKEN=False
FRONTEND_URL=https://SEU-FRONTEND.vercel.app
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=seu_usuario_smtp
SMTP_PASS=sua_senha_smtp
SMTP_FROM=seu_email_remetente
SMTP_USE_TLS=True
```

Depois do primeiro deploy, rode as migracoes no banco de producao usando a mesma `DATABASE_URL`:

```bash
python manage.py migrate
python manage.py seed
```

Na Vercel, o upload de arquivos para `/media/` nao deve ser usado como armazenamento permanente. Em producao, configure `CLOUDINARY_URL` para que os uploads de imagem sejam salvos no Cloudinary. As imagens locais continuam funcionando apenas na demonstracao local com `SERVE_MEDIA=True`.

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

Recuperacao de senha:

- Se `SMTP_HOST` estiver configurado, a API envia um e-mail com link para `FRONTEND_URL/redefinir-senha`.
- Se `SMTP_HOST` estiver vazio, o Django usa backend de console e imprime a mensagem no log do servidor.
- Em desenvolvimento, `PASSWORD_RESET_EXPOSE_TOKEN=True` tambem retorna `uid` e `token` na resposta para facilitar testes locais.
- Em producao, use `PASSWORD_RESET_EXPOSE_TOKEN=False`.

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
- Sem `CLOUDINARY_URL`, o projeto usa armazenamento local para facilitar os testes de desenvolvimento.

Testado em producao na Vercel em 26/06/2026:

- Raiz `https://puc-encontra-api.vercel.app/` redireciona para `/api/docs/`.
- Swagger abre em `https://puc-encontra-api.vercel.app/api/docs/`.
- `GET /api/`, `GET /api/objetos/`, `GET /api/categorias/` e `GET /api/locais/` retornaram `200`.
- CORS respondeu corretamente para `https://puc-encontra-frontend.vercel.app`.
- Login com `admin` e `aluno1` retornou token.
- Admin acessou `/api/usuarios/`; usuario comum recebeu `403`, como esperado.
- Smoke test de CRUD criou, editou, marcou como resolvido e apagou um objeto temporario.
- Smoke test de CRUD criou e removeu categoria/local temporarios.
- O armazenamento persistente de imagens em producao fica disponivel quando `CLOUDINARY_URL` esta configurada no ambiente da API.

## O Que Nao Funcionou ou Esta Pendente

- O envio real de e-mail para recuperacao de senha depende das variaveis SMTP configuradas no ambiente de producao.
- Para testar upload persistente em producao, configure `CLOUDINARY_URL` na Vercel e redeploye a API.
- Ainda nao ha testes automatizados; os testes feitos foram manuais via curl, navegador e Swagger.

## Comandos de Validacao

```bash
SERVE_MEDIA=True python manage.py check
curl http://127.0.0.1:8000/api/
curl http://127.0.0.1:8000/api/schema/
curl http://127.0.0.1:8000/api/docs/
```

## Observacoes Para Entrega

O backend esta publicado na Vercel em [https://puc-encontra-api.vercel.app/](https://puc-encontra-api.vercel.app/) e usa banco PostgreSQL Neon em producao.
