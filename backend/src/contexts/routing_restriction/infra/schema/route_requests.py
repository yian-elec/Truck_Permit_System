"""
route_requests — ORM 對應 routing.route_requests。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RouteRequests(Base):
    """路線申請主檔（起訖點文字與可選 Point 幾何）。"""

    __tablename__ = "route_requests"
    __table_args__ = {"schema": "routing"}

    route_request_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    origin_text = Column(String(255), nullable=False)
    origin_point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    destination_text = Column(String(255), nullable=False)
    destination_point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    requested_departure_at = Column(DateTime(timezone=True), nullable=True)
    vehicle_weight_ton = Column(Numeric(8, 2), nullable=True)
    vehicle_kind = Column(String(50), nullable=True)
    status = Column(String(30), nullable=False)
    # 地理編碼失敗原因（與領域 RouteRequest.geocode_failure_reason 對齊；不可 silent fail）
    geocode_failure_reason = Column(Text, nullable=True)
    requested_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
