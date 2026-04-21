"""
rule_geometries — ORM 對應 routing.rule_geometries。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RuleGeometries(Base):
    """規則對應之空間圖徵（PostGIS geometry，SRID 4326）。"""

    __tablename__ = "rule_geometries"
    __table_args__ = {"schema": "routing"}

    geometry_id = Column(UUID(as_uuid=True), primary_key=True)
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.restriction_rules.rule_id"),
        nullable=False,
    )
    geom = Column(Geometry(srid=4326), nullable=False)
    bbox = Column(Geometry(srid=4326), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
