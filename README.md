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


## API de lançamentos financeiros

Endpoints protegidos por `Authorization: Bearer <token>`:

- `POST /financial-entries`: cria um lançamento financeiro para a empresa do usuário autenticado.
- `GET /financial-entries`: lista lançamentos somente da empresa autenticada.
- `GET /financial-entries/{entry_id}`: consulta um lançamento da empresa autenticada.
- `PUT /financial-entries/{entry_id}`: atualiza um lançamento da empresa autenticada.
- `DELETE /financial-entries/{entry_id}`: remove um lançamento da empresa autenticada.

Exemplo de criação:

```bash
curl -X POST http://localhost:8000/financial-entries \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "revenue",
    "category": "balcão",
    "description": "Vendas do dia",
    "amount": 850.50,
    "payment_method": "pix",
    "entry_date": "2026-06-09",
    "source": "manual"
  }'
```

Filtros simples de listagem:

- `type`: `revenue` ou `expense`;
- `start_date`: data inicial no formato `YYYY-MM-DD`;
- `end_date`: data final no formato `YYYY-MM-DD`.

Dashboard, cálculos de lucro, ponto de equilíbrio, relatórios e gráficos ainda não foram implementados.

## API de custos fixos do negócio

Endpoints protegidos por `Authorization: Bearer <token>`:

- `POST /business-costs`: cria um custo fixo mensal para a empresa do usuário autenticado.
- `GET /business-costs`: lista custos fixos somente da empresa autenticada.
- `GET /business-costs/{cost_id}`: consulta um custo fixo da empresa autenticada.
- `PUT /business-costs/{cost_id}`: atualiza um custo fixo da empresa autenticada.
- `DELETE /business-costs/{cost_id}`: remove um custo fixo da empresa autenticada.

Exemplo de criação:

```bash
curl -X POST http://localhost:8000/business-costs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aluguel",
    "category": "aluguel",
    "amount": 2500.00,
    "is_active": true,
    "notes": "Ponto comercial"
  }'
```

Filtro simples de listagem:

- `is_active`: `true` para custos ativos ou `false` para custos inativos.

Exemplos:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/business-costs
curl -H "Authorization: Bearer <token>" "http://localhost:8000/business-costs?is_active=true"
curl -H "Authorization: Bearer <token>" "http://localhost:8000/business-costs?is_active=false"
```

Ponto de equilíbrio e necessidade mínima de faturamento ainda não foram implementados.

## API de resumo de custos fixos

Endpoint protegido por `Authorization: Bearer <token>`:

- `GET /business-cost-summary`: resume os custos fixos mensais cadastrados para a empresa do usuário autenticado.

Exemplo:

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/business-cost-summary
```

Exemplo de resposta:

```json
{
  "total_active_monthly_costs": 3700.0,
  "active_costs_count": 4,
  "inactive_costs_count": 1,
  "total_costs_count": 5,
  "status": "configured"
}
```

Custos inativos não entram em `total_active_monthly_costs`. Ponto de equilíbrio ainda não foi implementado.

## API de resumo financeiro

Endpoint protegido por `Authorization: Bearer <token>`:

- `GET /financial-summary`: resume receitas, despesas, saldo e status do período para a empresa do usuário autenticado.

Parâmetros opcionais de query string:

- `start_date`: data inicial no formato `YYYY-MM-DD`;
- `end_date`: data final no formato `YYYY-MM-DD`.

Exemplos:

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/financial-summary

curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/financial-summary?start_date=2026-06-01&end_date=2026-06-30"
```

Exemplo de resposta:

```json
{
  "total_revenue": 2500.0,
  "total_expense": 1800.0,
  "net_result": 700.0,
  "status": "positive",
  "entries_count": 12,
  "start_date": "2026-06-01",
  "end_date": "2026-06-30"
}
```

Dashboard, ponto de equilíbrio, margem por produto e IA ainda não foram implementados.

A tela autenticada `/app` exibe um resumo financeiro simples consumindo `/financial-summary` e um resumo simples de custos fixos consumindo `/business-cost-summary`. Ponto de equilíbrio, gráficos, margem por produto e IA ainda não foram implementados.

### Frontend

Configure a URL pública da API usada pelo Next.js:

```bash
export NEXT_PUBLIC_API_URL="http://localhost:8000"
```

Também é possível usar o valor de referência do `.env.example`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para rodar a aplicação:

```bash
cd frontend
npm install
npm run dev
```

A página inicial fica disponível em `http://localhost:3000`.

Fluxo manual de autenticação:

1. Acesse `http://localhost:3000/register`, preencha os dados do usuário e da empresa e confirme o redirecionamento para `/app`.
2. Use o botão **Sair** para remover o token local.
3. Acesse `http://localhost:3000/login`, entre com o e-mail e senha cadastrados e confirme o retorno para `/app`.

A tela `/app` mostra a base da conta criada e tem um link para `/app/entries`.

Fluxo manual de lançamentos financeiros:

1. Acesse `/app/entries` com uma sessão ativa.
2. Cadastre uma receita ou despesa informando tipo, categoria, valor, forma de pagamento e data.
3. Use o filtro **Todos**, **Receitas** ou **Despesas** para listar lançamentos por tipo.
4. Use **Excluir** em um card para remover um lançamento.

Dashboard financeiro, cálculos de lucro, ponto de equilíbrio, relatórios, gráficos e IA ainda não foram implementados.

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

## Tela de custos fixos

A área autenticada inclui a rota `/app/business-costs` para cadastrar e acompanhar custos fixos mensais do negócio.

Fluxo manual sugerido:

1. Entrar na aplicação e acessar `/app/business-costs` pelo botão “Cadastrar custos fixos” na área inicial.
2. Criar um custo fixo informando nome, categoria, valor mensal, status ativo e observações opcionais.
3. Conferir a listagem em cards e alternar os filtros Todos, Ativos e Inativos.
4. Usar o botão Ativar/Desativar para mudar o status de um custo.
5. Usar o botão Excluir e confirmar a remoção quando necessário.

Ponto de equilíbrio ainda não foi implementado nesta tela.
