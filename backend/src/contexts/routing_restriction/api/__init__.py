"""
Routing_Restriction context — API 層。

匯出申請人、審查、管理三組路由器，於 `main.py` 掛載；路由僅依賴 App 層 DTO 與服務。
"""

from .routes import (
    routing_admin_router,
    routing_applicant_router,
    routing_review_router,
)

__all__ = [
    "routing_applicant_router",
    "routing_review_router",
    "routing_admin_router",
]
