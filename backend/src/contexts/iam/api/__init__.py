"""
iam api — IAM Context 之 FastAPI 路由匯出。

API 實作集中於 `routes.py`；請與 `main.py` 以 `include_router` 掛載。
"""

from __future__ import annotations

from .routes import router as iam_router

__all__ = ["iam_router"]
