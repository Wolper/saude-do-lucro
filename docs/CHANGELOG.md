# Changelog

## 2026-06-09

### Added

- Autenticação básica com registro, login, JWT e rotas protegidas.
- Cadastro da empresa inicial junto com a criação do usuário.
- Models SQLAlchemy para `users` e `companies` com relacionamento `companies.owner_id -> users.id`.
- Migration Alembic inicial para criação das tabelas `users` e `companies`.
- Telas simples `/register`, `/login` e `/app` no frontend.
- Testes backend para registro, e-mail duplicado, login, rota `/auth/me` e empresa atual.
