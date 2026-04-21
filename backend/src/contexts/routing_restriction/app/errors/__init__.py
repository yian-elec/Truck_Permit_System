"""
Routing_Restriction 應用層錯誤匯出。

實作集中於 **routing_app_errors.py**（命名對齊 Application context 之 *application_app_errors.py*）：
統一繼承 `BaseError`、對應 HTTP status_code，並提供 `to_routing_app_error` 供服務層捕捉後轉換。
"""

from .routing_app_errors import (
    RoutingAppError,
    RoutingConflictAppError,
    RoutingFeatureNotReadyAppError,
    RoutingNotFoundAppError,
    RoutingValidationAppError,
    map_routing_domain_to_app,
    to_routing_app_error,
)

__all__ = [
    "RoutingAppError",
    "RoutingConflictAppError",
    "RoutingFeatureNotReadyAppError",
    "RoutingNotFoundAppError",
    "RoutingValidationAppError",
    "map_routing_domain_to_app",
    "to_routing_app_error",
]
