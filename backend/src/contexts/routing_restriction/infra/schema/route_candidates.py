"""
route_candidates — ORM 對應 routing.route_candidates。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RouteCandidates(Base):
    """單一候選路線（LineString 4326）。"""

    __tablename__ = "route_candidates"
    __table_args__ = {"schema": "routing"}

    candidate_id = Column(UUID(as_uuid=True), primary_key=True)
    route_plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.route_plans.route_plan_id"),
        nullable=False,
    )
    candidate_rank = Column(Integer, nullable=False)
    distance_m = Column(Integer, nullable=False)
    duration_s = Column(Integer, nullable=False)
    score = Column(Numeric(10, 4), nullable=False)
    summary_text = Column(Text, nullable=True)
    area_road_sequence = Column(JSONB, nullable=True)
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
