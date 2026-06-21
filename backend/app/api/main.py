"""FastAPI application entry point."""
import os as _os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api import campaigns, content, intent, ws, agent

app = FastAPI(title="AdCockpit v2 API", version="2.0.0")

# ── CORS ──────────────────────────────────────────────────────────────
_cors_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    _os.getenv("CORS_ORIGIN", ""),
    "https://*.vercel.app",
]
_cors_origins = [o for o in _cors_origins if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins if _cors_origins else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Key Auth (simple, no DB needed) ───────────────────────────────
_API_SECRET = _os.getenv("API_SECRET_KEY", "")

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # Only protect /api/* routes; skip /health, /docs, /openapi.json
    path = request.url.path
    if path.startswith("/api/") and _API_SECRET:
        # Skip auth for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        client_key = request.headers.get("X-API-Key", "")
        if client_key != _API_SECRET:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid API key. Add X-API-Key header."},
            )
    return await call_next(request)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(campaigns.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(intent.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
