"""
road_source_batches — Overpass/OSM 抓取批次（routing.road_source_batches）。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RoadSourceBatches(Base):
    """一次道路資料抓取任務之詮釋資料。"""

    __tablename__ = "road_source_batches"
    __table_args__ = {"schema": "routing"}

    batch_id = Column(UUID(as_uuid=True), primary_key=True)
    source_type = Column(String(30), nullable=False)  # osm_overpass
    query_signature = Column(String(255), nullable=False)
    bbox_geom = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    origin_point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    destination_point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    query_text = Column(Text, nullable=False)
    source_generated_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), nullable=False)
    record_count = Column(Integer, nullable=False, server_default="0")
    parse_skipped_count = Column(Integer, nullable=False, server_default="0")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
