"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import campaigns, content, intent, ws, agent

app = FastAPI(title="AdCockpit v2 API", version="2.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(campaigns.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(intent.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
