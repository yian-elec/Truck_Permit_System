"""
RouteRequest — 路線申請聚合根。

責任：維護與通行證案件關聯之路線請求（起訖文字、期望出發時間、車輛條件、申請人），
以及地理編碼與送規劃之狀態機；確保「geocode 失敗可終止、成功才可進入規劃佇列」等不變條件。
不負責實際呼叫 Geocoding API（由 App 層呼叫後回填領域狀態）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.contexts.routing_restriction.domain.errors import (
    GeocodingRequiredError,
    InvalidRouteRequestStateError,
    RoutingInvalidValueError,
)
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
    RouteRequestStatus,
)
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import (
    VehicleConstraint,
)


@dataclass
class RouteRequest:
    """
    路線申請（對應 routing.route_requests）。

    責任邊界：
    - 持有 **application_id** 與唯讀語意之 **route_request_id**。
    - **origin_text / destination_text** 為使用者輸入；**origin_point / destination_point** 於 geocode 成功後填入。
    - **vehicle_profile** 封裝車重與車種，供後續規則比對。
    - **status** 驅動 UC-ROUTE-01 成敗與是否可觸發 UC-ROUTE-02。
    """

    route_request_id: UUID
    application_id: UUID
    origin_text: str
    destination_text: str
    status: RouteRequestStatus
    vehicle_profile: VehicleConstraint = field(default_factory=VehicleConstraint)
    requested_departure_at: Optional[datetime] = None
    requested_by: Optional[UUID] = None
    origin_point: Optional[GeoPoint] = None
    destination_point: Optional[GeoPoint] = None
    geocode_failure_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.origin_text.strip() or not self.destination_text.strip():
            raise RoutingInvalidValueError("origin_text and destination_text must be non-empty")

    @classmethod
    def submit_new(
        cls,
        *,
        route_request_id: UUID,
        application_id: UUID,
        origin_text: str,
        destination_text: str,
        vehicle_profile: VehicleConstraint,
        requested_departure_at: Optional[datetime],
        requested_by: Optional[UUID],
        now: datetime,
    ) -> RouteRequest:
        """
        建立新路線申請（UC-ROUTE-01 領域部分：寫入業務欄位與初始狀態）。

        責任：初始為 PENDING_GEOCODE；座標欄位為空直至 App 回填 geocode 結果。
        **map／planning 版本**由 `RoutePlan` 持有，不在本聚合。
        """
        return cls(
            route_request_id=route_request_id,
            application_id=application_id,
            origin_text=origin_text,
            destination_text=destination_text,
            status=RouteRequestStatus.PENDING_GEOCODE,
            vehicle_profile=vehicle_profile,
            requested_departure_at=requested_departure_at,
            requested_by=requested_by,
            origin_point=None,
            destination_point=None,
            geocode_failure_reason=None,
            created_at=now,
            updated_at=now,
        )

    def start_geocoding(self, now: datetime) -> None:
        """標記進入地理編碼處理中。"""
        if self.status not in (
            RouteRequestStatus.PENDING_GEOCODE,
            RouteRequestStatus.GEOCODE_FAILED,
        ):
            raise InvalidRouteRequestStateError(
                "Cannot start geocoding from current state",
                current_status=self.status.value,
            )
        self.status = RouteRequestStatus.GEOCODING
        self.updated_at = now

    def complete_geocoding_success(
        self,
        *,
        origin: GeoPoint,
        destination: GeoPoint,
        now: datetime,
    ) -> None:
        """地理編碼成功：寫入座標並允許後續排程規劃。"""
        if self.status != RouteRequestStatus.GEOCODING:
            raise InvalidRouteRequestStateError(
                "Geocoding success only allowed when status is GEOCODING",
                current_status=self.status.value,
            )
        self.origin_point = origin
        self.destination_point = destination
        self.geocode_failure_reason = None
        self.status = RouteRequestStatus.READY_TO_PLAN
        self.updated_at = now

    def complete_geocoding_failure(self, *, reason: str, now: datetime) -> None:
        """
        地理編碼失敗：標記失敗並保存原因（不可 silent fail）。

        責任：狀態轉為 GEOCODE_FAILED；不寫入有效座標。
        """
        if self.status != RouteRequestStatus.GEOCODING:
            raise InvalidRouteRequestStateError(
                "Geocoding failure only allowed when status is GEOCODING",
                current_status=self.status.value,
            )
        self.geocode_failure_reason = reason
        self.status = RouteRequestStatus.GEOCODE_FAILED
        self.updated_at = now

    def enqueue_planning(self, now: datetime) -> None:
        """
        將申請送入規劃佇列（UC-ROUTE-01 成功路徑末尾）。

        責任：必須已具備起訖座標；觸發後狀態 PLANNING_QUEUED，由 App 非同步執行 UC-ROUTE-02。
        """
        if self.origin_point is None or self.destination_point is None:
            raise GeocodingRequiredError(
                "Cannot enqueue planning without resolved origin and destination points"
            )
        if self.status != RouteRequestStatus.READY_TO_PLAN:
            raise InvalidRouteRequestStateError(
                "Planning queue only from READY_TO_PLAN",
                current_status=self.status.value,
            )
        self.status = RouteRequestStatus.PLANNING_QUEUED
        self.updated_at = now
