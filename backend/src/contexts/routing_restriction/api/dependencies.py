"""
Routing_Restriction API — 依賴注入。

責任：提供 `RoutingApplicationService` 單例式工廠（每請求新建實例亦可，目前無狀態）；
承辦／申請人之使用者 UUID 沿用 Application API 之 JWT 解析，避免重複實作。
"""

from __future__ import annotations

from src.contexts.routing_restriction.app.services.routing_application_service import (
    RoutingApplicationService,
)


def get_routing_application_service() -> RoutingApplicationService:
    """取得路線與限制情境之應用服務（Facade）。"""
    return RoutingApplicationService()
