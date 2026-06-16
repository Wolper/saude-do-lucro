from fastapi import FastAPI

from app.api.routes import (
    auth,
    break_even_summary,
    business_cost_summary,
    business_costs,
    companies,
    financial_entries,
    financial_summary,
    products,
)

app = FastAPI(title="Saude do Lucro API", version="0.1.0")
app.include_router(auth.router)
app.include_router(break_even_summary.router)
app.include_router(companies.router)
app.include_router(business_costs.router)
app.include_router(business_cost_summary.router)
app.include_router(financial_entries.router)
app.include_router(financial_summary.router)
app.include_router(products.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "saude-do-lucro-api",
        "version": "0.1.0",
    }
