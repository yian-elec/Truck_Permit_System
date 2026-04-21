"""
route_rule_hits — ORM 對應 routing.route_rule_hits。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RouteRuleHits(Base):
    """候選路線之規則命中紀錄。"""

    __tablename__ = "route_rule_hits"
    __table_args__ = {"schema": "routing"}

    rule_hit_id = Column(UUID(as_uuid=True), primary_key=True)
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.route_candidates.candidate_id"),
        nullable=False,
    )
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.restriction_rules.rule_id"),
        nullable=False,
    )
    hit_type = Column(String(30), nullable=False)
    # 不設 FK 至 route_segments：允許先寫 hit 後補 segment；由 App 維護一致性。
    segment_id = Column(UUID(as_uuid=True), nullable=True)
    detail_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
