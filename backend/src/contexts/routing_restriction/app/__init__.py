"""
Routing_Restriction — App 層（用例服務、DTO、錯誤）。

目錄結構（`app` 根下三個主目錄，與 Application context 對齊）：

- **dtos/**：輸入／輸出資料傳輸物件（Pydantic），依角色或 UC 分檔。
- **errors/**：應用層錯誤型別與領域例外映射（對應 `routing_app_errors.py`）。
- **services/**：用例服務、出站埠（**`services/ports/`**）、Facade **`RoutingApplicationService`**。

責任：協調領域與 Infra，實作 UC-ROUTE-01～06；不包含 HTTP 路由（見 api 層）。
"""

from . import dtos, errors, services
from .errors import (
    RoutingAppError,
    RoutingConflictAppError,
    RoutingFeatureNotReadyAppError,
    RoutingNotFoundAppError,
    RoutingValidationAppError,
    to_routing_app_error,
)
from .services import RoutingApplicationService

__all__ = [
    "RoutingApplicationService",
    "RoutingAppError",
    "RoutingConflictAppError",
    "RoutingFeatureNotReadyAppError",
    "RoutingNotFoundAppError",
    "RoutingValidationAppError",
    "dtos",
    "errors",
    "services",
    "to_routing_app_error",
]
