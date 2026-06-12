# Saúde do Lucro

Fundação do projeto **Saúde do Lucro**, um copiloto de lucratividade para pequenos negócios de alimentação.

## Stack oficial

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS e App Router.
- **Backend:** FastAPI e Python.
- **Banco de dados:** PostgreSQL via Docker Compose com volume persistente.

## Estrutura principal

```text
backend/
  app/api/routes/auth.py
  app/api/routes/companies.py
  app/core/config.py
  app/core/database.py
  app/core/security.py
  app/main.py
  app/models/
  app/schemas/
  app/services/
  migrations/
  requirements.txt
  tests/test_health.py
frontend/
  app/layout.tsx
  app/page.tsx
  app/globals.css
  package.json
  next.config.ts
  tailwind.config.ts
  postcss.config.mjs
  tsconfig.json
docs/project-guidelines.md
docker-compose.yml
```

## Como rodar localmente

### Banco de dados

```bash
docker compose up -d postgres
```

Configure a URL de conexão usada pelo backend e pelo Alembic e as variáveis de JWT:

```bash
export DATABASE_URL="postgresql+psycopg://saude_user:saude_password@localhost:5432/saude_do_lucro"
export JWT_SECRET_KEY="change-me-in-development"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"
```

Use um valor seguro para `JWT_SECRET_KEY` fora do ambiente de desenvolvimento.

Para aplicar as migrations:

```bash
cd backend
alembic upgrade head
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{
  "status": "ok",
  "service": "saude-do-lucro-api",
  "version": "0.1.0"
}
```


## API de autenticação

Nesta etapa foram implementados apenas endpoints backend. O frontend de cadastro/login ainda não foi implementado.

Endpoints disponíveis:

- `POST /auth/register`: cria um usuário com senha hasheada e uma empresa inicial vinculada.
- `POST /auth/login`: autentica e retorna um token JWT Bearer.
- `GET /auth/me`: retorna o usuário autenticado.
- `GET /companies/current`: retorna a empresa atual do usuário autenticado.

Exemplo de cadastro:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João",
    "email": "joao@email.com",
    "password": "senha_segura",
    "company_name": "MM Chicken",
    "segment": "hamburgueria",
    "city": "São Paulo",
    "state": "SP"
  }'
```

Exemplo de login:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@email.com", "password": "senha_segura"}'
```

Use o `access_token` retornado no header `Authorization: Bearer <token>` para consultar `/auth/me` e `/companies/current`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

A página inicial fica disponível em `http://localhost:3000`.

## Testes

### Backend

```bash
cd backend
PYTHONPATH=. python -m pytest
```


### Frontend

```bash
cd frontend
npm run build
```

## Diretrizes do projeto

As diretrizes longas de produto, arquitetura e escopo estão em [`docs/project-guidelines.md`](docs/project-guidelines.md).
