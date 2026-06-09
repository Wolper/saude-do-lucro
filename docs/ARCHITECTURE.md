# Arquitetura

## Fundação inicial

A aplicação começa como um monólito modular separado por pastas principais:

- `frontend/`: aplicação Next.js com App Router, React, TypeScript e Tailwind CSS.
- `backend/`: API FastAPI em Python.
- `docs/`: documentação de produto, arquitetura, decisões e roadmap.
- `docker-compose.yml`: PostgreSQL local para desenvolvimento.

## Backend

O backend expõe inicialmente apenas `GET /health`, com configuração por variáveis de ambiente e CORS para desenvolvimento local.

## Frontend

O frontend tem uma página inicial mobile first que comunica a proposta do produto e tenta consultar a saúde da API por `NEXT_PUBLIC_API_URL` sem quebrar caso o backend esteja indisponível.

## Banco de dados

PostgreSQL roda via Docker Compose com volume persistente. Nesta fundação não há migrations nem schema de negócio.

## Multiempresa

O produto será SaaS no futuro. Entidades de negócio futuras devem considerar isolamento por `company_id`.
