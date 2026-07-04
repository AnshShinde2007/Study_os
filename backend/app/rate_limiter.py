import time
import asyncio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .config import settings

class RateLimiter:
    def __init__(self, limit: int, window: int = 60):
        self.limit = limit
        self.window = window
        self.requests: dict[str, list[float]] = {}  # ip -> list of timestamps
        self.lock = asyncio.Lock()

    async def is_allowed(self, client_ip: str) -> tuple[bool, int, int]:
        """
        Check if client_ip is allowed under the rate limit.
        Returns:
            (is_allowed: bool, remaining_requests: int, reset_time_seconds: int)
        """
        async with self.lock:
            now = time.time()
            cutoff = now - self.window
            
            # Clean up old timestamps
            timestamps = self.requests.get(client_ip, [])
            timestamps = [t for t in timestamps if t > cutoff]
            self.requests[client_ip] = timestamps
            
            if len(timestamps) < self.limit:
                # Allow request
                timestamps.append(now)
                remaining = self.limit - len(timestamps)
                # Next reset is when the oldest timestamp falls outside the window
                reset_in = int(self.window - (now - timestamps[0])) if timestamps else self.window
                return True, remaining, max(0, reset_in)
            else:
                # Rate limited
                remaining = 0
                reset_in = int(self.window - (now - timestamps[0]))
                return False, remaining, max(0, reset_in)

class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = None):
        super().__init__(app)
        limit = limit if limit is not None else settings.rate_limit_per_minute
        self.limiter = RateLimiter(limit=limit)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Determine client IP address (check X-Forwarded-For if behind a reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        allowed, remaining, reset_in = await self.limiter.is_allowed(client_ip)

        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={"message": "Too many requests. Please try again later.", "code": "rate_limited"}
            )
            response.headers["X-RateLimit-Limit"] = str(self.limiter.limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(reset_in)
            response.headers["Retry-After"] = str(reset_in)
            return response

        # Proceed to next middleware/endpoint
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        return response
