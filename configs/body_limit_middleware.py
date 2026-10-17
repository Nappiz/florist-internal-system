from collections import deque
import re

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class BodyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int = 16_384):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        receipt = scope.get("method") == "POST" and re.fullmatch(r"/api/v1/expenses/[0-9a-fA-F-]{36}/receipts", scope.get("path", "")) is not None
        internal_configuration = scope.get("method") in {"POST", "PUT", "PATCH"} and re.fullmatch(r"/api/v1/(?:custom-bouquets(?:/estimate|/[0-9a-fA-F-]{36})?|bouquet-options(?:/[0-9a-fA-F-]{36})?|cashflow/backfill)", scope.get("path", "")) is not None
        max_bytes = 5 * 1024 * 1024 if receipt else 256 * 1024 if internal_configuration else self.max_bytes
        messages = deque()
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            total += len(message.get("body", b""))
            if total > max_bytes:
                await JSONResponse({"detail": "Request body terlalu besar."}, status_code=413)(scope, receive, send)
                return
            messages.append(message)
            if not message.get("more_body", False):
                break

        async def replay_receive():
            if messages:
                return messages.popleft()
            return await receive()

        await self.app(scope, replay_receive, send)
