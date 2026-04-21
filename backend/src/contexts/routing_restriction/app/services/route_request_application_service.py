"""
UC-ROUTE-01：建立路線申請、地理編碼、排程自動規劃前置狀態。

責任：
- 組裝領域 RouteRequest 並單次交易寫入（避免狀態機中途提交）。
- 呼叫 GeocodingPort；失敗寫入原因，成功則 enqueue_planning。
- 不直接觸發 UC-ROUTE-02（可由 API 層或非同步 worker 呼叫規劃服務）。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.routing_restriction.app.dtos.route_request_dtos import (
    CreateRouteRequestInputDTO,
    RouteRequestStatusDTO,
)
from src.contexts.routing_restriction.app.errors import to_routing_app_error
from src.contexts.routing_restriction.app.services.ports.outbound import (
    GeocodeResolution,
    GeocodingPort,
)
from src.contexts.routing_restriction.domain.entities.route_request import RouteRequest
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import (
    VehicleConstraint,
)
from src.contexts.routing_restriction.infra.repositories.route_request_repository import (
    RouteRequestRepository,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _merge_geocode_failure_reasons(
    o: GeocodeResolution, d: GeocodeResolution
) -> str:
    """兩點無法同時解析時寫入單一原因；優先具體子原因（如 nominatim_*）。"""
    if o.point is None and o.failure_reason:
        return o.failure_reason
    if d.point is None and d.failure_reason:
        return d.failure_reason
    return "geocoding_failed: origin or destination could not be resolved"


class RouteRequestApplicationService:
    """路線申請用例服務。"""

    def __init__(
        self,
        *,
        route_requests: RouteRequestRepository | None = None,
        geocoding: GeocodingPort | None = None,
    ) -> None:
        self._requests = route_requests or RouteRequestRepository()
        self._geocoding = geocoding
        if self._geocoding is None:
            from src.contexts.routing_restriction.infra.geocoding.geocoding_factory import (
                build_geocoding_port_from_settings,
            )

            self._geocoding = build_geocoding_port_from_settings()

    def create_route_request(
        self,
        application_id: UUID,
        dto: CreateRouteRequestInputDTO,
        *,
        requested_by: UUID | None,
    ) -> RouteRequestStatusDTO:
        """
        建立新路線申請並嘗試地理編碼；成功則狀態至 planning_queued。

        責任：單次 `save` 前完成狀態機轉移，確保失敗原因可追溯。
        """
        now = _utc_now()
        rid = uuid4()
        vehicle = VehicleConstraint(
            weight_ton=dto.vehicle_weight_ton,
            kind=dto.vehicle_kind,
        )
        try:
            req = RouteRequest.submit_new(
                route_request_id=rid,
                application_id=application_id,
                origin_text=dto.origin_text,
                destination_text=dto.destination_text,
                vehicle_profile=vehicle,
                requested_departure_at=dto.requested_departure_at,
                requested_by=requested_by,
                now=now,
            )
            req.start_geocoding(now)
            dto_has_coords = (
                dto.origin_lat is not None
                and dto.origin_lon is not None
                and dto.destination_lat is not None
                and dto.destination_lon is not None
            )
            if dto_has_coords:
                o_pt = GeoPoint(
                    latitude=dto.origin_lat,
                    longitude=dto.origin_lon,
                )
                d_pt = GeoPoint(
                    latitude=dto.destination_lat,
                    longitude=dto.destination_lon,
                )
                req.complete_geocoding_success(origin=o_pt, destination=d_pt, now=now)
                req.enqueue_planning(now=now)
            else:
                o_res = self._geocoding.resolve_point(req.origin_text)
                d_res = self._geocoding.resolve_point(req.destination_text)
                if o_res.point is None or d_res.point is None:
                    reason = _merge_geocode_failure_reasons(o_res, d_res)
                    req.complete_geocoding_failure(reason=reason, now=now)
                else:
                    req.complete_geocoding_success(
                        origin=o_res.point,
                        destination=d_res.point,
                        now=now,
                    )
                    req.enqueue_planning(now=now)
            self._requests.save(req)
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

        return self._to_status_dto(self._requests.get_by_id(rid))

    def replan_route_request(
        self,
        application_id: UUID,
        dto: CreateRouteRequestInputDTO,
        *,
        requested_by: UUID | None,
    ) -> RouteRequestStatusDTO:
        """
        重新申請路線（語意：新起訖／條件再以 UC-ROUTE-01 流程處理）。

        責任：實作上建立**新** route_request 列，保留歷史於舊列。
        """
        return self.create_route_request(
            application_id,
            dto,
            requested_by=requested_by,
        )

    def get_route_request_status(
        self,
        application_id: UUID,
    ) -> RouteRequestStatusDTO | None:
        """同一案件最新路線申請狀態；無則 None。"""
        req = self._requests.find_latest_by_application_id(application_id)
        if req is None:
            return None
        return self._to_status_dto(req)

    def _to_status_dto(self, req: RouteRequest | None) -> RouteRequestStatusDTO:
        if req is None:
            raise ValueError("route request missing after save")
        return RouteRequestStatusDTO(
            route_request_id=req.route_request_id,
            application_id=req.application_id,
            status=req.status.value,
            origin_text=req.origin_text,
            destination_text=req.destination_text,
            geocode_failure_reason=req.geocode_failure_reason,
            requested_departure_at=req.requested_departure_at,
            vehicle_weight_ton=req.vehicle_profile.weight_ton,
            vehicle_kind=req.vehicle_profile.kind,
        )
