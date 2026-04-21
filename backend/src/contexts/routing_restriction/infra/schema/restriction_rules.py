"""
restriction_rules — ORM 對應 routing.restriction_rules。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RestrictionRules(Base):
    """限制規則主檔（關聯 map_layers）。"""

    __tablename__ = "restriction_rules"
    __table_args__ = {"schema": "routing"}

    rule_id = Column(UUID(as_uuid=True), primary_key=True)
    layer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.map_layers.layer_id"),
        nullable=False,
    )
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False)
    weight_limit_ton = Column(Numeric(8, 2), nullable=True)
    direction = Column(String(20), nullable=True)
    time_rule_text = Column(Text, nullable=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    priority = Column(Integer, nullable=False, server_default="100")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
