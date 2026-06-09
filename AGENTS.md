# AGENTS.md — Instruções para Codex

## Projeto

Este repositório contém o projeto **Saúde do Lucro**, aplicação SaaS também chamada internamente de **Copiloto de Saúde Financeira e Lucratividade**.

O produto ajuda pequenos negócios de alimentação a entender se estão lucrando, qual é o ponto de equilíbrio, quais produtos sustentam o resultado e quais decisões podem melhorar a lucratividade.

## Regras obrigatórias

- Nunca fazer merge automático na `main`.
- Nunca commitar diretamente na `main`.
- Nunca adicionar funcionalidades fora do escopo da tarefa.
- Nunca transformar o produto em ERP.
- Não implementar autenticação, IA, dashboard real, fiscal, estoque avançado, WhatsApp, cardápio digital, pedidos online ou integrações externas sem autorização explícita.
- Manter a arquitetura simples, modular e validável.
- Priorizar velocidade de validação e uso real na MM Chicken.

## Stack preferencial

- Frontend: Next.js, React, TypeScript e Tailwind CSS.
- Backend: FastAPI e Python.
- Banco de dados: PostgreSQL.

## Multiempresa

O produto será SaaS e multiempresa. Entidades futuras de negócio devem considerar isolamento por `company_id` quando aplicável.

## Entrega

Ao finalizar uma tarefa, informe branch, resumo, arquivos criados/alterados, como rodar, como testar, testes executados, pendências, riscos e próximos passos.
