# Backend — Saúde do Lucro

API inicial em FastAPI para o Saúde do Lucro.

## Requisitos

- Python 3.11+
- PostgreSQL local via Docker Compose (opcional nesta fundação; ainda não há schema)

## Instalação

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rodar localmente

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testar saúde da API

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
