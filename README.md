# Saude do Lucro

Fundacao do projeto **Saude do Lucro**, um copiloto de lucratividade para pequenos negocios de alimentacao.

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

Configure a URL de conexao usada pelo backend e pelo Alembic e as variaveis de JWT:

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


## API de autenticacao

Endpoints disponiveis:

- `POST /auth/register`: cria um usuario com senha hasheada e uma empresa inicial vinculada.
- `POST /auth/login`: autentica e retorna um token JWT Bearer.
- `GET /auth/me`: retorna o usuario autenticado.
- `GET /companies/current`: retorna a empresa atual do usuario autenticado.

Exemplo de cadastro:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Joao",
    "email": "joao@email.com",
    "password": "senha_segura",
    "company_name": "MM Chicken",
    "segment": "hamburgueria",
    "city": "Sao Paulo",
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


## API de lancamentos financeiros

Endpoints protegidos por `Authorization: Bearer <token>`:

- `POST /financial-entries`: cria um lancamento financeiro para a empresa do usuario autenticado.
- `GET /financial-entries`: lista lancamentos somente da empresa autenticada.
- `GET /financial-entries/{entry_id}`: consulta um lancamento da empresa autenticada.
- `PUT /financial-entries/{entry_id}`: atualiza um lancamento da empresa autenticada.
- `DELETE /financial-entries/{entry_id}`: remove um lancamento da empresa autenticada.

Exemplo de criacao:

```bash
curl -X POST http://localhost:8000/financial-entries \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "revenue",
    "category": "balcao",
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

Dashboard, calculos de lucro, ponto de equilibrio, relatorios e graficos ainda nao foram implementados.

## API de custos fixos do negocio

Endpoints protegidos por `Authorization: Bearer <token>`:

- `POST /business-costs`: cria um custo fixo mensal para a empresa do usuario autenticado.
- `GET /business-costs`: lista custos fixos somente da empresa autenticada.
- `GET /business-costs/{cost_id}`: consulta um custo fixo da empresa autenticada.
- `PUT /business-costs/{cost_id}`: atualiza um custo fixo da empresa autenticada.
- `DELETE /business-costs/{cost_id}`: remove um custo fixo da empresa autenticada.

Exemplo de criacao:

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


## API de produtos

Endpoints protegidos por `Authorization: Bearer <token>`:

- `POST /products`: cria um produto para a empresa do usuario autenticado.
- `GET /products`: lista produtos somente da empresa autenticada.
- `GET /products/unit-margin-ranking`: lista produtos ordenados pela maior margem unitaria.
- `GET /products/{product_id}`: consulta um produto da empresa autenticada.
- `PUT /products/{product_id}`: atualiza um produto da empresa autenticada.
- `DELETE /products/{product_id}`: remove um produto da empresa autenticada.

Campos principais:

- `name`: nome do produto.
- `category`: categoria do produto.
- `selling_price`: preco de venda.
- `estimated_unit_cost`: custo unitario estimado.
- `is_active`: indica se o produto esta ativo.
- `notes`: observacoes opcionais.

A resposta inclui `unit_margin`, `margin_percent` e `pricing_status`.
O `pricing_status` pode ser `profitable`, `break_even` ou `loss`.

Filtros de listagem:

- `is_active`: `true` para ativos ou `false` para inativos.
- `category`: categoria exata do produto.

Ranking de margem unitaria:

- `GET /products/unit-margin-ranking` usa `is_active=true` por padrao.
- `limit` usa padrao 10 e maximo 50.
- `category` tambem pode ser usado no ranking.

Exemplo de criacao:

```bash
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "X Burger",
    "category": "hamburguer",
    "selling_price": 30.00,
    "estimated_unit_cost": 12.50,
    "is_active": true,
    "notes": "Produto principal"
  }'
```

Exemplos:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/products
curl -H "Authorization: Bearer <token>" "http://localhost:8000/products?is_active=true&category=hamburguer"
curl -H "Authorization: Bearer <token>" "http://localhost:8000/products/unit-margin-ranking?limit=10"
```

## API de resumo de custos fixos

Endpoint protegido por `Authorization: Bearer <token>`:

- `GET /business-cost-summary`: resume os custos fixos mensais cadastrados para a empresa do usuario autenticado.

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

Custos inativos nao entram em `total_active_monthly_costs`.

## API de ponto de equilibrio simplificado

Endpoint protegido por `Authorization: Bearer <token>`:

- `GET /break-even-summary`: resume a cobertura dos custos fixos ativos pela receita da empresa autenticada.

Parametros opcionais de query string:

- `start_date`: data inicial no formato `YYYY-MM-DD`;
- `end_date`: data final no formato `YYYY-MM-DD`.

Exemplo:

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/break-even-summary?start_date=2026-06-01&end_date=2026-06-30"
```

Exemplo de resposta:

```json
{
  "monthly_fixed_costs": 3700.0,
  "break_even_revenue": 3700.0,
  "period_revenue": 2500.0,
  "revenue_gap": 1200.0,
  "coverage_percent": 67.57,
  "status": "below_break_even",
  "active_costs_count": 4,
  "revenue_entries_count": 12,
  "start_date": "2026-06-01",
  "end_date": "2026-06-30",
  "method": "fixed_cost_coverage",
  "note": "Calculo simplificado: considera apenas custos fixos ativos e receitas do periodo. Nao considera margem por produto, custos variaveis ou CMV."
}
```

Este e um calculo simplificado de cobertura de custos fixos: a receita necessaria para cobrir custos fixos e igual a soma dos custos fixos ativos mensais. Margem por produto, CMV, custos variaveis e IA ainda nao foram implementados.

## API de resumo financeiro

Endpoint protegido por `Authorization: Bearer <token>`:

- `GET /financial-summary`: resume receitas, despesas, saldo e status do periodo para a empresa do usuario autenticado.

Parametros opcionais de query string:

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

Dashboard, graficos, margem por produto e IA ainda nao foram implementados.

A tela autenticada `/app` exibe um resumo financeiro simples consumindo `/financial-summary`, um resumo simples de custos fixos consumindo `/business-cost-summary` e um ponto de equilibrio simplificado consumindo `/break-even-summary`. Esse calculo ainda considera apenas custos fixos ativos e receitas registradas; graficos, margem por produto, CMV, custos variaveis e IA ainda nao foram implementados.

### Frontend

Configure a URL publica da API usada pelo Next.js:

```bash
export NEXT_PUBLIC_API_URL="http://localhost:8000"
```

Tambem e possivel usar o valor de referencia do `.env.example`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para rodar a aplicacao:

```bash
cd frontend
npm install
npm run dev
```

A pagina inicial fica disponivel em `http://localhost:3000`.

Fluxo manual de autenticacao:

1. Acesse `http://localhost:3000/register`, preencha os dados do usuario e da empresa e confirme o redirecionamento para `/app`.
2. Use o botao **Sair** para remover o token local.
3. Acesse `http://localhost:3000/login`, entre com o e-mail e senha cadastrados e confirme o retorno para `/app`.

A tela `/app` mostra a base da conta criada e tem um link para `/app/entries`.

Fluxo manual de lancamentos financeiros:

1. Acesse `/app/entries` com uma sessao ativa.
2. Cadastre uma receita ou despesa informando tipo, categoria, valor, forma de pagamento e data.
3. Use o filtro **Todos**, **Receitas** ou **Despesas** para listar lancamentos por tipo.
4. Use **Excluir** em um card para remover um lancamento.

Dashboard financeiro, calculos de lucro, ponto de equilibrio, relatorios, graficos e IA ainda nao foram implementados.

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

As diretrizes longas de produto, arquitetura e escopo estao em [`docs/project-guidelines.md`](docs/project-guidelines.md).

## Tela de custos fixos

A area autenticada inclui a rota `/app/business-costs` para cadastrar e acompanhar custos fixos mensais do negocio.

Fluxo manual sugerido:

1. Entrar na aplicacao e acessar `/app/business-costs` pelo botao Cadastrar custos fixos na area inicial.
2. Criar um custo fixo informando nome, categoria, valor mensal, status ativo e observacoes opcionais.
3. Conferir a listagem em cards e alternar os filtros Todos, Ativos e Inativos.
4. Usar o botao Ativar/Desativar para mudar o status de um custo.
5. Usar o botao Excluir e confirmar a remocao quando necessario.

Ponto de equilibrio ainda nao foi implementado nesta tela.
