import json
from collections.abc import Awaitable, Callable
from typing import Any

API_VERSION = "0.1.0"
SERVICE_NAME = "saude-do-lucro-api"

HEALTH_RESPONSE = {
    "status": "ok",
    "service": SERVICE_NAME,
    "version": API_VERSION,
}

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] != "http":
        return

    if scope.get("method") == "GET" and scope.get("path") == "/health":
        body = json.dumps(HEALTH_RESPONSE).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": body})
        return

    await send(
        {
            "type": "http.response.start",
            "status": 404,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": b'{"detail":"Not Found"}'})
