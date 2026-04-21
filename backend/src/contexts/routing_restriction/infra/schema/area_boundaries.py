"""
area_boundaries — 行政區界（僅供區名輸出／查詢，不參與禁區避讓）。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class AreaBoundaries(Base):
    """行政區或多邊形區域（WGS84 MultiPolygon）。"""

    __tablename__ = "area_boundaries"
    __table_args__ = (
        Index("idx_area_boundaries_area_name", "area_name"),
        {"schema": "routing"},
    )

    area_id = Column(UUID(as_uuid=True), primary_key=True)
    area_name = Column(String(100), nullable=False)
    area_code = Column(String(50), nullable=True)
    geom = Column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=False,
    )
    is_active = Column(Boolean, nullable=False, server_default="true")
    source_type = Column(String(30), nullable=False)
    source_ref = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
