"""
road_edges — 道路段明細（routing.road_edges），供 MVP 路網組候選查詢。
"""

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RoadEdges(Base):
    """單一道路段（對應 OSM way 第一版 segment_index=0）。"""

    __tablename__ = "road_edges"
    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "osm_way_id",
            "segment_index",
            name="uq_road_edges_batch_way_seg",
        ),
        Index("idx_road_edges_batch_id", "batch_id"),
        Index("idx_road_edges_osm_way_id", "osm_way_id"),
        Index("idx_road_edges_highway_type", "highway_type"),
        # GiST on geom / bbox_geom：由 GeoAlchemy2 Geometry(spatial_index=True，預設) 建立
        # idx_road_edges_geom、idx_road_edges_bbox_geom；勿再於此重複宣告同名 Index（會 DuplicateTable）。
        {"schema": "routing"},
    )

    road_edge_id = Column(UUID(as_uuid=True), primary_key=True)
    batch_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.road_source_batches.batch_id"),
        nullable=False,
    )
    source_type = Column(String(30), nullable=False)
    osm_element_type = Column(String(20), nullable=False)
    osm_way_id = Column(BigInteger, nullable=False)
    segment_index = Column(Integer, nullable=False, server_default="0")
    road_name = Column(String(255), nullable=False)
    road_ref = Column(String(100), nullable=True)
    highway_type = Column(String(100), nullable=False)
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    bbox_geom = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    node_count = Column(Integer, nullable=False)
    length_m = Column(Integer, nullable=False)
    raw_tags_json = Column(JSONB, nullable=False)
    raw_payload_fragment = Column(JSONB, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
