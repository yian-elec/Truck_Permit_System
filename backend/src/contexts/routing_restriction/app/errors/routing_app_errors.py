"""
Routing_Restriction 應用層錯誤型別。

責任：集中管理 HTTP 對應語意；將領域例外（RoutingDomainError）映射為可序列化之 BaseError 子類。
"""

from __future__ import annotations

from shared.errors.base_error.base_error import BaseError


class RoutingAppError(BaseError):
    """路線／限制應用層錯誤基底（預設 422）。"""

    @property
    def status_code(self) -> int:
        return 422


class RoutingNotFoundAppError(RoutingAppError):
    """資源不存在（404）。"""

    @property
    def status_code(self) -> int:
        return 404


class RoutingValidationAppError(RoutingAppError):
    """輸入驗證失敗（400）。"""

    @property
    def status_code(self) -> int:
        return 400


class RoutingConflictAppError(RoutingAppError):
    """狀態衝突（409）。"""

    @property
    def status_code(self) -> int:
        return 409


class RoutingFeatureNotReadyAppError(RoutingAppError):
    """功能尚未接好外部作業／儲存（501）。"""

    @property
    def status_code(self) -> int:
        return 501


def map_routing_domain_to_app(exc: BaseException) -> RoutingAppError:
    """將領域例外映射為應用層錯誤。"""
    from src.contexts.routing_restriction.domain.errors import (
        CandidateNotInPlanError,
        GeocodingRequiredError,
        InvalidRoutePlanStateError,
        InvalidRouteRequestStateError,
        RoutingDomainError,
        RoutingInvalidValueError,
    )

    if isinstance(exc, RoutingInvalidValueError):
        return RoutingValidationAppError(exc.message, exc.details)
    if isinstance(exc, InvalidRouteRequestStateError):
        return RoutingConflictAppError(exc.message, exc.details)
    if isinstance(exc, InvalidRoutePlanStateError):
        return RoutingConflictAppError(exc.message, exc.details)
    if isinstance(exc, CandidateNotInPlanError):
        return RoutingValidationAppError(exc.message, exc.details)
    if isinstance(exc, GeocodingRequiredError):
        return RoutingConflictAppError(exc.message, exc.details)
    if isinstance(exc, RoutingDomainError):
        return RoutingAppError(exc.message, exc.details)
    return RoutingAppError(str(exc), None)


def to_routing_app_error(exc: BaseException) -> RoutingAppError:
    """統一入口：已是 App 錯誤則直接回傳；LookupError → 404；領域例外 → 映射。"""
    if isinstance(exc, RoutingAppError):
        return exc
    if isinstance(exc, LookupError):
        return RoutingNotFoundAppError(str(exc), details={"kind": "lookup_error"})
    from src.contexts.routing_restriction.domain.errors import RoutingDomainError

    if isinstance(exc, RoutingDomainError):
        return map_routing_domain_to_app(exc)
    details = getattr(exc, "details", None)
    if isinstance(details, dict):
        return RoutingAppError(str(exc), details)
    return RoutingAppError(str(exc), None)
