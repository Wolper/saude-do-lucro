# Saúde do Lucro

Fundação do projeto **Saúde do Lucro**, um copiloto de lucratividade para pequenos negócios de alimentação.

## Stack oficial

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS e App Router.
- **Backend:** FastAPI, SQLAlchemy, Pydantic, Alembic e Python.
- **Banco de dados:** PostgreSQL via Docker Compose com volume persistente.
- **Autenticação:** JWT com senha hasheada via bcrypt/passlib.

## Estrutura principal

```text
backend/
  alembic.ini
  app/
    main.py
    core/
      config.py
      database.py
      security.py
    api/routes/
      auth.py
      companies.py
      health.py
    models/
      user.py
      company.py
    schemas/
      auth.py
      user.py
      company.py
    services/
      auth_service.py
  migrations/
    versions/20260609_0001_create_users_companies.py
  requirements.txt
  tests/
frontend/
  app/
    page.tsx
    register/page.tsx
    login/page.tsx
    app/page.tsx
  package.json
docs/
  project-guidelines.md
  CHANGELOG.md
docker-compose.yml
.env.example
```

## Variáveis de ambiente

Copie `.env.example` para `.env` quando necessário e ajuste os valores locais:

```bash
cp .env.example .env
```

Variáveis do backend:

- `DATABASE_URL`: URL SQLAlchemy do PostgreSQL.
- `JWT_SECRET_KEY`: segredo usado para assinar JWTs. Trocar em produção.
- `JWT_ALGORITHM`: algoritmo do JWT. Padrão: `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: duração do token em minutos.

Variável opcional do frontend:

- `NEXT_PUBLIC_API_URL`: URL pública do backend. Se ausente, o frontend usa `http://localhost:8000`.

## Como rodar localmente

### Banco de dados

```bash
docker compose up -d postgres
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

### Migrations

Com o PostgreSQL rodando e `DATABASE_URL` configurada:

```bash
cd backend
alembic upgrade head
```

Para criar uma nova migration futuramente:

```bash
cd backend
alembic revision --autogenerate -m "descricao da mudanca"
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

A página inicial fica disponível em `http://localhost:3000`.

## Endpoints de autenticação e empresa

### `POST /auth/register`

Cria usuário e empresa inicial.

```json
{
  "name": "João",
  "email": "joao@email.com",
  "password": "senha_segura",
  "company_name": "MM Chicken",
  "segment": "hamburgueria",
  "city": "São Paulo",
  "state": "SP"
}
```

### `POST /auth/login`

Autentica usuário e retorna token JWT.

```json
{
  "email": "joao@email.com",
  "password": "senha_segura"
}
```

### `GET /auth/me`

Retorna o usuário autenticado. Requer header:

```bash
Authorization: Bearer <token>
```

### `GET /companies/current`

Retorna a empresa do usuário autenticado. Requer header:

```bash
Authorization: Bearer <token>
```

## Como testar autenticação manualmente

```bash
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"João","email":"joao@email.com","password":"senha_segura","company_name":"MM Chicken","segment":"hamburgueria","city":"São Paulo","state":"SP"}'
```

Guarde o `access_token` retornado e consulte a conta:

```bash
curl http://localhost:8000/auth/me \
  -H 'Authorization: Bearer <token>'
```

Consulte a empresa atual:

```bash
curl http://localhost:8000/companies/current \
  -H 'Authorization: Bearer <token>'
```

## Testes

### Backend

```bash
cd backend
PYTHONPATH=. python -m pytest
```

Os testes de autenticação usam SQLite em memória para manter a execução leve, enquanto a aplicação continua configurada para PostgreSQL em produção.

### Frontend

```bash
cd frontend
npm run build
```

## Diretrizes do projeto

As diretrizes longas de produto, arquitetura e escopo estão em [`docs/project-guidelines.md`](docs/project-guidelines.md).
