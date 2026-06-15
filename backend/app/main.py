from fastapi import FastAPI

from app.api.routes import auth, companies, financial_entries, financial_summary

app = FastAPI(title="Saúde do Lucro API", version="0.1.0")
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(financial_entries.router)
app.include_router(financial_summary.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "saude-do-lucro-api",
        "version": "0.1.0",
    }
