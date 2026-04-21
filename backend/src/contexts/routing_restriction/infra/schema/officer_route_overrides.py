"""
officer_route_overrides — ORM 對應 routing.officer_route_overrides。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class OfficerRouteOverrides(Base):
    """承辦人工改線。"""

    __tablename__ = "officer_route_overrides"
    __table_args__ = {"schema": "routing"}

    override_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    base_candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.route_candidates.candidate_id"),
        nullable=True,
    )
    override_geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    override_reason = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
