import asyncio
import json

from app.main import app


def test_health_check_returns_service_status() -> None:
    messages = []

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(
        app(
            {
                "type": "http",
                "method": "GET",
                "path": "/health",
                "headers": [],
            },
            receive,
            send,
        )
    )

    assert messages[0]["status"] == 200
    assert json.loads(messages[1]["body"]) == {
        "status": "ok",
        "service": "saude-do-lucro-api",
        "version": "0.1.0",
    }
