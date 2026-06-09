# Saúde do Lucro

Fundação do projeto **Saúde do Lucro**, um copiloto de lucratividade para pequenos negócios de alimentação.

## Stack oficial

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS e App Router.
- **Backend:** FastAPI e Python.
- **Banco de dados:** PostgreSQL via Docker Compose com volume persistente.

## Estrutura principal

```text
backend/
  app/main.py
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
pytest
```

### Frontend

```bash
cd frontend
npm run build
```

## Diretrizes do projeto

As diretrizes longas de produto, arquitetura e escopo estão em [`docs/project-guidelines.md`](docs/project-guidelines.md).
