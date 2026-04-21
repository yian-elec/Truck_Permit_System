"""
Routing_Restriction 專屬領域錯誤。

責任：表達路線申請狀態機、規劃聚合不變條件、候選歸屬等違例；供 App 層對應 HTTP／錯誤碼。
僅繼承 `DomainError`，不依賴 Infra / App / API。
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from shared.errors.domain_error import DomainError


class RoutingDomainError(DomainError):
    """
    Routing_Restriction 領域錯誤基底。

    責任：統一本 context 內業務規則違例的父類型。
    """

    pass


class RoutingInvalidValueError(RoutingDomainError):
    """
    值物件或欄位不符合領域約束（座標範圍、版本字串空白、排序重複等）。

    責任：在聚合／VO 建構或轉移時立即失敗，避免不合法資料進入後續規劃流程。
    """

    pass


class InvalidRouteRequestStateError(RoutingDomainError):
    """
    路線申請（RouteRequest）當前狀態不允許所請求的領域行為。

    責任：例如尚未 geocode 成功卻標記為可規劃、或已失敗仍強制送規劃任務。
    """

    def __init__(
        self,
        message: str,
        *,
        current_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        d = dict(details or {})
        if current_status is not None:
            d["current_status"] = current_status
        super().__init__(message, d if d else None)


class InvalidRoutePlanStateError(RoutingDomainError):
    """
    路線規劃聚合（RoutePlan）狀態不允許選線、改線或重算等操作。

    責任：例如尚無候選卻選定 candidate、已標記 no_route 仍寫入選定結果等。
    """

    def __init__(
        self,
        message: str,
        *,
        current_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        d = dict(details or {})
        if current_status is not None:
            d["current_status"] = current_status
        super().__init__(message, d if d else None)


class CandidateNotInPlanError(RoutingDomainError):
    """
    指定的候選路線不屬於當前 RoutePlan。

    責任：承辦選線或人工改線時，防止跨案件／跨計畫誤綁 candidate。
    """

    def __init__(
        self,
        message: str,
        *,
        candidate_id: Optional[UUID] = None,
        route_plan_id: Optional[UUID] = None,
    ) -> None:
        details: Dict[str, Any] = {}
        if candidate_id is not None:
            details["candidate_id"] = str(candidate_id)
        if route_plan_id is not None:
            details["route_plan_id"] = str(route_plan_id)
        super().__init__(message, details if details else None)


class GeocodingRequiredError(RoutingDomainError):
    """
    必須先完成起訖點地理編碼（或標記失敗）才能進行後續步驟。

    責任：約束「先解析座標、再送規劃」的流程順序，與 UC-ROUTE-01 對齊。
    """

    pass
