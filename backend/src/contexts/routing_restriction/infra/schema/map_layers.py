"""
map_layers — ORM 對應 routing.map_layers（圖資版本／layer）。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class MapLayers(Base):
    """地圖圖資層次與版本（KML 匯入後一筆 layer 版本）。"""

    __tablename__ = "map_layers"
    __table_args__ = {"schema": "routing"}

    layer_id = Column(UUID(as_uuid=True), primary_key=True)
    layer_code = Column(String(50), nullable=False)
    layer_name = Column(String(100), nullable=False)
    layer_type = Column(String(30), nullable=False)
    source_type = Column(String(30), nullable=False)
    source_ref = Column(String(255), nullable=True)
    version_no = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="false")
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
