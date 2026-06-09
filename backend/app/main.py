from fastapi import FastAPI

app = FastAPI(title="Saúde do Lucro API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "saude-do-lucro-api",
        "version": "0.1.0",
    }
