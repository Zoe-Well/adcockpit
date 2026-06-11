"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.sse_manager import SSEManager


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AdCockpit API",
        description="AI 数字营销对话驾驶舱 — LangGraph Agent 后端",
        version="1.0.0",
    )

    # CORS — allow Streamlit dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://localhost:3000",
            "*",  # Allow all origins in demo mode
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize SSE Manager on app state
    app.state.sse_manager = SSEManager()

    # Include routes
    app.include_router(router)

    return app


# Module-level app instance for uvicorn
app = create_app()
