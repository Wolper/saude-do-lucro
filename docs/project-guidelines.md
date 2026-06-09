# Diretrizes do projeto — Saúde do Lucro

## Projeto

Este repositório contém o projeto **Saúde do Lucro**, aplicação SaaS também chamada internamente de **Copiloto de Saúde Financeira e Lucratividade**.

O produto ajuda pequenos negócios de alimentação — restaurantes, trailers, hamburguerias, pizzarias, lanchonetes, açaiterias, food trucks e negócios familiares — a entender se estão lucrando, qual é o ponto de equilíbrio, quais produtos sustentam o resultado, quais preços precisam ser corrigidos e quais decisões podem melhorar a lucratividade.

O objetivo central é:

> Ajudar o pequeno empresário de alimentação a saber se o negócio está saudável, quanto precisa vender para sobreviver e quais decisões aumentam sua lucratividade.

---

## Papel do Codex

O Codex deve atuar como executor técnico das tarefas definidas pelo fundador e pelo LUCRO Builder.

O Codex não deve tomar decisões estratégicas sozinho, não deve expandir escopo sem autorização e não deve transformar o produto em um ERP complexo.

Sempre que receber uma tarefa, deve:

1. Criar uma branch própria.
2. Implementar apenas o escopo solicitado.
3. Manter a arquitetura simples e modular.
4. Criar ou ajustar testes quando aplicável.
5. Atualizar documentação quando houver alteração relevante.
6. Abrir Pull Request.
7. Informar claramente arquivos alterados, comandos de teste, pendências e riscos.

---

## Regras obrigatórias de trabalho

- Nunca fazer merge automático na `main`.
- Nunca commitar diretamente na `main`.
- Nunca remover funcionalidades existentes sem justificativa clara.
- Nunca adicionar funcionalidades fora do escopo da tarefa.
- Nunca implementar integrações externas sem solicitação explícita.
- Nunca transformar o sistema em ERP.
- Nunca criar módulos fiscais complexos no MVP.
- Nunca criar estoque avançado no MVP.
- Nunca criar WhatsApp, cardápio digital, pedidos online ou integrações com delivery no MVP.
- Sempre manter o produto simples, direto e útil para tomada de decisão financeira.
- Sempre priorizar velocidade de validação e uso real na MM Chicken.

---

## Stack técnica preferencial

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- App Router

### Backend

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- Alembic (quando migrations forem autorizadas)

### Banco de dados

- PostgreSQL

### Arquitetura

Usar monólito modular.

Não usar microserviços no MVP.

A aplicação deve ser separada internamente por domínios, mas mantendo simplicidade operacional.

Domínios previstos:

- auth
- companies
- financial_entries
- business_structure
- ingredients
- purchases
- products
- recipes
- profitability
- health_metrics
- ai_consultant
- alerts

---

## Princípios do produto

Toda funcionalidade deve responder positivamente a pelo menos uma destas perguntas:

1. Ajuda o negócio a entender se está lucrando?
2. Ajuda a entender a saúde financeira?
3. Ajuda a calcular ponto de equilíbrio?
4. Ajuda a entender margem, custo ou preço?
5. Ajuda a tomar uma decisão prática de lucratividade?

Se a resposta for não, a funcionalidade deve ser adiada.

---

## Escopo do MVP

O MVP pode conter:

- Cadastro de empresa.
- Usuários e autenticação.
- Lançamentos financeiros.
- Receitas.
- Despesas.
- Custos fixos.
- Custos variáveis.
- Metas.
- Ponto de equilíbrio.
- Falta para empatar.
- Falta para meta.
- Meta diária necessária.
- Ingredientes.
- Compras de ingredientes.
- Custo médio móvel.
- Produtos.
- Fichas técnicas simples.
- Custo unitário estimado.
- Lucro unitário estimado.
- Margem por produto.
- Saúde financeira do negócio.
- Radar de rentabilidade.
- Alertas simples.
- Consultor IA baseado em dados reais.

---

## Fora do MVP

Não implementar sem autorização explícita:

- NFC-e.
- SPED.
- Contabilidade avançada.
- Estoque avançado.
- Controle de lote.
- Controle de validade.
- Integração bancária.
- Integração com iFood.
- Integração com delivery.
- WhatsApp.
- Cardápio digital.
- Pedidos online.
- Marketplace.
- Folha de pagamento completa.
- Aplicativo mobile nativo.
- Microserviços.
- Mensageria complexa.
- BI avançado.
- Relatórios contábeis complexos.

---

## Regras de negócio principais

### Receita

Entrada de dinheiro, como:

- PIX
- cartão
- dinheiro
- delivery
- balcão

### Despesa

Saída de dinheiro, como:

- aluguel
- energia
- água
- salários
- contador
- manutenção
- combustível
- compra de insumos

### Custos fixos

Gastos recorrentes que existem mesmo se vender pouco, como:

- aluguel
- salários
- internet
- contador
- financiamento
- pró-labore
- sistemas

### Custos variáveis

Gastos que variam conforme venda, como:

- taxa de cartão
- taxa de delivery
- embalagem
- comissão
- insumos
- imposto estimado sobre venda

### Custo médio móvel

Para cada ingrediente, calcular custo médio com base nas compras registradas.

Preferir média ponderada por quantidade.

Se não houver quantidade suficiente para média ponderada, usar média simples como fallback.

### Produto

Produto pode ter:

- preço de venda
- ingredientes
- quantidades
- perdas
- embalagens
- adicionais
- taxas
- imposto estimado

### Custo do produto

O custo do produto é a soma dos custos estimados dos ingredientes e insumos utilizados.

### Lucro unitário estimado

Lucro unitário estimado = preço de venda - custo estimado do produto.

### Margem do produto

Margem do produto = lucro unitário estimado / preço de venda.

### Ponto de equilíbrio

Ponto de equilíbrio = custos fixos mensais / margem média de contribuição.

### Meta diária necessária

Meta diária necessária = valor faltante para o objetivo / dias restantes no período.

---

## Classificações

Usar classificações simples:

- Verde: saudável.
- Amarelo: atenção.
- Vermelho: perigo.

Evitar falsa precisão contábil.

Quando o cálculo for estimado, informar que é estimado.

---

## IA

A IA deve funcionar como consultora financeiro-operacional.

A IA pode ajudar com:

- interpretação de lançamentos;
- classificação de despesas;
- explicação de indicadores;
- recomendações práticas;
- simulações;
- alertas;
- respostas estratégicas.

A IA não deve inventar dados.

Se não houver dados suficientes, responder claramente que faltam informações e pedir apenas o mínimo necessário.

Estrutura preferencial das respostas da IA:

1. Diagnóstico.
2. Número principal.
3. Explicação.
4. Recomendação prática.
5. Nível de confiança, quando aplicável.

---

## UI e UX

O público é usuário não técnico, pequeno empresário e com pouco tempo.

A interface deve ser:

- simples;
- direta;
- mobile first;
- com linguagem de negócio;
- sem excesso de gráficos;
- sem jargão contábil desnecessário;
- sem formulários complexos.

Preferir textos como:

- “Quanto falta vender”
- “Negócio saudável”
- “Produto em atenção”
- “Preço pode estar defasado”
- “Falta para empatar”
- “Falta para meta”

Evitar no MVP termos como:

- EBITDA
- DRE
- centro de custo
- regime fiscal avançado

---

## Dashboard principal esperado

O dashboard principal deve priorizar:

- faturamento do mês;
- despesas do mês;
- lucro estimado;
- ponto de equilíbrio;
- falta para meta;
- produto mais lucrativo;
- principal alerta;
- recomendação prática.

Não criar dashboard excessivamente complexo.

---

## Multi-tenant

O produto será SaaS.

Todos os dados de negócio devem ser isolados por empresa.

Entidades de negócio devem usar `company_id` quando aplicável.

Nunca permitir acesso cruzado entre empresas.

Priorizar testes de isolamento por empresa quando houver autenticação e dados multiempresa.

---

## Banco de dados

Usar PostgreSQL.

Usar migrations controladas com Alembic.

Criar índices quando necessário, sem exagero.

Não criar schema complexo antes da necessidade real.

Entidades conceituais previstas:

- users
- companies
- financial_entries
- business_costs
- goals
- ingredients
- ingredient_purchases
- products
- product_recipes
- product_profitability
- alerts
- ai_recommendations

---

## Testes prioritários

Priorizar testes para:

- autenticação;
- isolamento por empresa;
- cálculo de custo médio;
- cálculo de margem;
- cálculo de lucro unitário;
- cálculo de ponto de equilíbrio;
- cálculo de metas;
- classificações verde/amarelo/vermelho;
- regras de acesso.

---

## Documentação

Atualizar documentação quando houver:

- funcionalidade implementada;
- regra alterada;
- decisão técnica tomada;
- tabela criada ou alterada;
- API criada;
- tela relevante criada;
- bug importante corrigido.

Documentos esperados ao longo do projeto:

- README.md
- PRODUCT_VISION.md
- ROADMAP.md
- PRODUCT_DECISIONS.md
- ARCHITECTURE.md
- DATABASE_SCHEMA.md
- BUSINESS_RULES.md
- FINANCIAL_HEALTH_MODEL.md
- METRICS_CATALOG.md
- AI_BEHAVIOR.md
- API_DOCUMENTATION.md
- USER_MANUAL.md
- ADMIN_MANUAL.md
- DEPLOY_GUIDE.md
- TESTING_GUIDE.md
- CHANGELOG.md

---

## Padrão de branches

Usar nomes claros:

- `chore/project-foundation`
- `feature/auth-companies`
- `feature/financial-entries`
- `feature/business-costs`
- `feature/products-recipes`
- `feature/profitability-calculations`
- `feature/financial-health-dashboard`
- `feature/ai-consultant`
- `fix/descricao-curta-do-bug`
- `docs/descricao-da-documentacao`

---

## Padrão de entrega

Ao finalizar uma tarefa, sempre informar:

1. Nome da branch.
2. Resumo do que foi feito.
3. Arquivos criados ou alterados.
4. Como rodar.
5. Como testar.
6. Testes executados.
7. Pendências.
8. Riscos técnicos.
9. Próximos passos recomendados.

---

## Restrições finais

Este projeto deve nascer simples, funcional e validável.

A prioridade é ajudar negócios reais de alimentação a tomar decisões melhores de lucratividade.

Não adicionar complexidade por antecipação.

Não criar funcionalidades “porque todo sistema tem”.

Só implementar o que ajuda diretamente na saúde financeira, lucratividade ou tomada de decisão.

---

## Autenticação e empresas — base SaaS

A base SaaS inicial possui autenticação simples por JWT e cadastro obrigatório de uma empresa inicial para cada usuário criado.

Regras desta fase:

- Cada usuário é dono de uma única empresa.
- `users.email` deve ser único.
- Senhas devem ser armazenadas somente como hash.
- Respostas da API nunca devem retornar `password_hash`.
- Rotas protegidas devem exigir token Bearer válido.
- Dados de negócio futuros devem carregar `company_id` para isolamento por empresa.

Endpoints atuais:

- `POST /auth/register`: cria usuário e empresa inicial.
- `POST /auth/login`: autentica e retorna JWT.
- `GET /auth/me`: retorna usuário autenticado.
- `GET /companies/current`: retorna empresa do usuário autenticado.

Migrations são controladas por Alembic em `backend/migrations` e devem ser executadas com `alembic upgrade head` a partir da pasta `backend`.
