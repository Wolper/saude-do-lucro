# Saúde do Lucro

Fundação técnica do **Saúde do Lucro**, um SaaS para ajudar pequenos negócios de alimentação a entender saúde financeira, ponto de equilíbrio, margem e decisões práticas de lucratividade.

## Escopo atual

Este repositório contém apenas a base técnica inicial do MVP:

- Backend ASGI compatível com Uvicorn e endpoint `GET /health`.
- Frontend web estático servido por Node.js, com tela inicial simples.
- Docker Compose para subir backend, frontend e PostgreSQL em ambiente local.
- Teste automatizado mínimo do endpoint de saúde.

Ainda **não** estão implementados autenticação, dashboard real, IA, banco com tabelas, migrations ou integrações externas.

## Estrutura

```text
backend/   API ASGI compatível com Uvicorn e testes automatizados
frontend/  Aplicação web estática servida por Node.js
docs/      Documentação de produto, escopo e diretrizes do projeto
```

## Requisitos locais

- Python 3.12+
- Node.js 20+
- npm
- Docker e Docker Compose, para validação completa com containers

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoint de saúde:

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

Testes:

```bash
cd backend
pytest
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:3000`. A stack preferencial documentada para evolução do produto segue em `docs/project-guidelines.md`; esta etapa mantém apenas uma tela estática mínima.

## Docker Compose

```bash
docker compose up -d
```

Serviços previstos:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Documentação do projeto

As diretrizes detalhadas de produto, escopo do MVP, regras de negócio e restrições foram preservadas em [`docs/project-guidelines.md`](docs/project-guidelines.md).
