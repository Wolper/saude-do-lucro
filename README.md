# Saúde do Lucro

O **Saúde do Lucro** é uma aplicação SaaS, também chamada internamente de **Copiloto de Saúde Financeira e Lucratividade**, para ajudar pequenos negócios de alimentação a entenderem se estão lucrando, qual é o ponto de equilíbrio, quais produtos sustentam o resultado e quais decisões podem melhorar a lucratividade.

O projeto prioriza simplicidade, validação rápida e uso real na MM Chicken. Ele **não deve virar ERP**.

## Stack técnica

- **Frontend:** Next.js, React, TypeScript e Tailwind CSS.
- **Backend:** FastAPI e Python tipado.
- **Banco:** PostgreSQL via Docker Compose.
- **Documentação:** Markdown em `docs/`.

## Estrutura de pastas

```text
saude-do-lucro/
  frontend/
  backend/
  docs/
  docker-compose.yml
  .env.example
  README.md
  AGENTS.md
```

## Variáveis de ambiente

Use `.env.example` como referência:

```bash
cp .env.example .env
```

Variáveis principais:

```env
POSTGRES_DB=saude_do_lucro
POSTGRES_USER=saude_user
POSTGRES_PASSWORD=saude_password
DATABASE_URL=postgresql://saude_user:saude_password@localhost:5432/saude_do_lucro
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Como rodar PostgreSQL

```bash
docker compose up -d
```

Verifique o status:

```bash
docker compose ps
```

Para parar:

```bash
docker compose down
```

## Como rodar o backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Como testar a rota `/health`

Com o backend rodando:

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

## Como rodar o frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Acesse:

```text
http://localhost:3000
```

A página inicial tenta consultar o backend em `GET /health`. Se a API estiver indisponível, a tela continua funcionando.

## O que está fora do MVP nesta fundação

Não foi implementado e não deve ser implementado sem autorização explícita:

- Autenticação.
- Dashboard financeiro real.
- IA.
- Schema completo de banco e migrations.
- Fiscal.
- Estoque avançado.
- WhatsApp.
- Cardápio digital.
- Pedidos online.
- Integrações externas, incluindo banco, iFood ou delivery.

## Documentação inicial

- `docs/PRODUCT_VISION.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/PRODUCT_DECISIONS.md`
- `docs/CHANGELOG.md`
