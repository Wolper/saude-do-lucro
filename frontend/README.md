# Frontend — Saúde do Lucro

Interface inicial em Next.js com App Router, TypeScript e Tailwind CSS.

## Instalação

```bash
cd frontend
npm install
```

## Variáveis de ambiente

Copie `.env.example` da raiz do projeto ou defina localmente:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Rodar localmente

```bash
npm run dev
```

Acesse `http://localhost:3000`.

A página tenta consultar `GET /health` no backend. Se a API não estiver disponível, a tela continua carregando normalmente.
