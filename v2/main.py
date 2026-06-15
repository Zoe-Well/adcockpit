"""AdCockpit v2 — FastAPI + Jinja2 frontend."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from v2.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="AdCockpit v2")

    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
    app.include_router(router)

    return app


app = create_app()
