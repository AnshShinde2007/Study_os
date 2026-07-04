from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .auth import router as auth_router
from .config import settings
from .functions import router as functions_router
from .rest import router as rest_router
from .storage import router as storage_router
from .memory_routes import router as memory_router
from .analytics_routes import router as analytics_router
from .graph_routes import router as graph_router
from .explainability_routes import router as explainability_router
from .adaptive_routes import router as adaptive_router
from .cognee.hackathon_routes import router as hackathon_router
from .cognee.hackathon_memory_routes import router as memory_tag_router
from .email_routes import router as email_router
from .rate_limiter import RateLimitingMiddleware

app = FastAPI(title="StudyOS API", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, https_only=False, same_site="lax")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"], expose_headers=["Content-Range"])
app.add_middleware(RateLimitingMiddleware)
app.include_router(auth_router); app.include_router(rest_router); app.include_router(storage_router); app.include_router(functions_router)
app.include_router(memory_router)
app.include_router(analytics_router)
app.include_router(graph_router)
app.include_router(explainability_router)
app.include_router(adaptive_router)
app.include_router(hackathon_router)
app.include_router(memory_tag_router)
app.include_router(email_router)

@app.get("/")
def health(): return {"status": "ok"}
