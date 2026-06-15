"""Main router — page routes + API aggregation."""
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from v2.api.campaigns import router as campaigns_router
from v2.api.content import router as content_router
from v2.api.intent import router as intent_router

router = APIRouter()

# API routes
router.include_router(campaigns_router, prefix="/api")
router.include_router(content_router, prefix="/api")
router.include_router(intent_router, prefix="/api")

# Cache the HTML template
_TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"
_CACHED_HTML = None


@router.get("/", response_class=HTMLResponse)
async def index():
    global _CACHED_HTML
    if _CACHED_HTML is None:
        _CACHED_HTML = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return _CACHED_HTML
