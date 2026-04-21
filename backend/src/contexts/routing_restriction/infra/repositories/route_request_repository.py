"""
RouteRequestRepository — routing.route_requests 持久化與領域映射。

責任：僅透過 `get_session` 交易；將 RouteRequest 聚合與 ORM 雙向轉換。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import select, text

from shared.core.db.connection import get_session

from src.contexts.routing_restriction.domain.entities.route_request import RouteRequest
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
    RouteRequestStatus,
)
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import (
    VehicleConstraint,
)
from src.contexts.routing_restriction.infra.repositories.geometry_wkt import (
    geo_point_to_point_wkt,
    parse_point_wkt,
)
from src.contexts.routing_restriction.infra.schema.route_requests import RouteRequests


def _point_wkt_element(p: GeoPoint) -> WKTElement:
    return WKTElement(geo_point_to_point_wkt(p), srid=4326)


def _row_to_domain_in_session(session, row: RouteRequests) -> RouteRequest:
    """於同一 session／交易內將 POINT 欄位轉成領域 GeoPoint。"""
    origin_pt: Optional[GeoPoint] = None
    dest_pt: Optional[GeoPoint] = None
    rid = row.route_request_id
    ow = session.execute(
        text("SELECT ST_AsText(origin_point) FROM routing.route_requests WHERE route_request_id = :rid"),
        {"rid": rid},
    ).scalar()
    if ow:
        origin_pt = parse_point_wkt(ow)
    dw = session.execute(
        text(
            "SELECT ST_AsText(destination_point) FROM routing.route_requests WHERE route_request_id = :rid"
        ),
        {"rid": rid},
    ).scalar()
    if dw:
        dest_pt = parse_point_wkt(dw)

    v = VehicleConstraint(
        weight_ton=Decimal(str(row.vehicle_weight_ton)) if row.vehicle_weight_ton is not None else None,
        kind=row.vehicle_kind,
    )
    return RouteRequest(
        route_request_id=row.route_request_id,
        application_id=row.application_id,
        origin_text=row.origin_text,
        destination_text=row.destination_text,
        status=RouteRequestStatus(row.status),
        vehicle_profile=v,
        requested_departure_at=row.requested_departure_at,
        requested_by=row.requested_by,
        origin_point=origin_pt,
        destination_point=dest_pt,
        geocode_failure_reason=row.geocode_failure_reason,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _apply_domain_to_row(row: RouteRequests, entity: RouteRequest) -> None:
    """將領域狀態寫回 ORM 列。"""
    row.application_id = entity.application_id
    row.origin_text = entity.origin_text
    row.destination_text = entity.destination_text
    row.requested_departure_at = entity.requested_departure_at
    row.vehicle_weight_ton = entity.vehicle_profile.weight_ton
    row.vehicle_kind = entity.vehicle_profile.kind
    row.status = entity.status.value
    row.requested_by = entity.requested_by
    row.geocode_failure_reason = entity.geocode_failure_reason
    row.origin_point = (
        _point_wkt_element(entity.origin_point) if entity.origin_point is not None else None
    )
    row.destination_point = (
        _point_wkt_element(entity.destination_point)
        if entity.destination_point is not None
        else None
    )
    row.updated_at = entity.updated_at


class RouteRequestRepository:
    """路線申請聚合之讀寫；交易由 `get_session` 自動提交／回滾。"""

    def save(self, entity: RouteRequest) -> None:
        """新增或更新單一路線申請。"""
        with get_session() as session:
            existing = session.get(RouteRequests, entity.route_request_id)
            if existing is None:
                row = RouteRequests(route_request_id=entity.route_request_id)
                _apply_domain_to_row(row, entity)
                row.created_at = entity.created_at
                session.add(row)
            else:
                _apply_domain_to_row(existing, entity)

    def get_by_id(self, route_request_id: UUID) -> Optional[RouteRequest]:
        with get_session() as session:
            row = session.get(RouteRequests, route_request_id)
            if row is None:
                return None
            return _row_to_domain_in_session(session, row)

    def find_latest_by_application_id(self, application_id: UUID) -> Optional[RouteRequest]:
        """同一案件最新一筆路線申請（依建立時間）。"""
        with get_session() as session:
            stmt = (
                select(RouteRequests)
                .where(RouteRequests.application_id == application_id)
                .order_by(RouteRequests.created_at.desc())
                .limit(1)
            )
            row = session.scalars(stmt).first()
            if row is None:
                return None
            return _row_to_domain_in_session(session, row)
