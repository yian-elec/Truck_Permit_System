"""
Integration_Operations — API 層。

導出 FastAPI `APIRouter`，供 `main` 掛載至 `/api/v1/ops/*`。
"""

from .routes import router as ops_router

__all__ = ["ops_router"]
