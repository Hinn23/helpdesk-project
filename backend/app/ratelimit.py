import os
import time
from collections import defaultdict
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.store = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if os.getenv("DISABLE_RATE_LIMIT"):
            return await call_next(request)
        if request.url.path == "/auth/login" and request.method == "POST":
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            timestamps = self.store[client_ip]
            timestamps[:] = [t for t in timestamps if now - t < self.window]
            if len(timestamps) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Слишком много попыток входа. Подождите минуту."},
                )
            timestamps.append(now)
        return await call_next(request)
