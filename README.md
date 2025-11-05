# CBF Manager - Backend

API REST desenvolvida com FastAPI para gerenciamento de operações da Confederação Brasileira de Futebol.

## Tecnologias

- **FastAPI** - Framework web de alta performance
- **SQLAlchemy** - ORM para banco de dados
- **Alembic** - Migração de banco de dados
- **Pydantic** - Validação de dados
- **JWT** - Autenticação baseada em tokens
- **Passlib** - Hash de senhas com bcrypt
- **Poetry** - Gerenciamento de dependências

## Instalação

### Pré-requisitos

- Python 3.12
- Poetry

### Instalar Dependências

```bash
cd backend/fastapi_core
poetry install
```

## Executar em Desenvolvimento

```bash
# Usando taskipy
task run

# Ou diretamente com uvicorn
poetry run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`

## Documentação da API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Testes

```bash
# Executar testes
task test

# Apenas linting
task lint

# Formatar código
task format
```

## Estrutura do Projeto

```
app/
├── app.py          # Aplicação principal e rotas
├── config.py       # Configurações e variáveis de ambiente
├── database.py     # Configuração do banco de dados
├── models.py       # Modelos SQLAlchemy
├── schemas.py      # Schemas Pydantic
├── crud.py         # Operações de banco de dados
└── security.py     # Autenticação e segurança
```

## Variáveis de Ambiente

Crie um arquivo `.env` baseado no `ienv.exemple`:

```env
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@cbfmanager.com
ADMIN_PASSWORD=sua-senha-admin-super-segura-aqui
ADMIN_NAME=Administrador CBF
CORS_ORIGINS_RAW=http://localhost:8000,http://localhost:9002
```

## Credenciais Padrão

⚠️ **Importante:** As credenciais padrão foram removidas da documentação por motivos de segurança. Consulte o arquivo `.env` para as variáveis de ambiente necessárias e defina senhas fortes e únicas para produção.

## Endpoints Principais

### Autenticação
- `POST /token` - Login e obtenção de token JWT
- `POST /register` - Registro de novo usuário
- `GET /users/me` - Dados do usuário autenticado

### Clubes
- `GET /clubs/` - Listar clubes
- `POST /clubs/` - Criar clube
- `GET /clubs/{id}` - Detalhes do clube

### Jogadores
- `GET /players/` - Listar jogadores
- `POST /players/` - Criar jogador
- `GET /players/{id}` - Detalhes do jogador
- `PUT /players/{id}` - Atualizar jogador
- `DELETE /players/{id}` - Excluir jogador

## Segurança

- Senhas com hash bcrypt
- Autenticação JWT com expiração
- CORS configurado
- Validação de dados com Pydantic
- Proteção de rotas sensíveis
