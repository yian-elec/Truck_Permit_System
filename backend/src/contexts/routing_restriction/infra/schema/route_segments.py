"""
route_segments — ORM 對應 routing.route_segments。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RouteSegments(Base):
    """候選路線之路段。"""

    __tablename__ = "route_segments"
    __table_args__ = {"schema": "routing"}

    segment_id = Column(UUID(as_uuid=True), primary_key=True)
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.route_candidates.candidate_id"),
        nullable=False,
    )
    seq_no = Column(Integer, nullable=False)
    road_name = Column(String(255), nullable=True)
    distance_m = Column(Integer, nullable=False)
    duration_s = Column(Integer, nullable=False)
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    instruction_text = Column(Text, nullable=True)
    is_exception_road = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
