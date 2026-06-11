"""Mock Server entry point — simulates巨量引擎 + 腾讯广告 + 小红书 etc.

Run: uvicorn mock_server.main:app --port 8100
"""
from fastapi import FastAPI
from mock_server.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ad Platform Mock Server",
        description="Simulates 巨量引擎 / 磁力引擎 / 腾讯广告 / 小红书聚光 / 飞书 / ERP APIs",
        version="1.0.0",
    )
    app.include_router(router)
    return app


app = create_app()
