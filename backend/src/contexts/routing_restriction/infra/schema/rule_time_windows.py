"""
rule_time_windows — ORM 對應 routing.rule_time_windows。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RuleTimeWindows(Base):
    """規則之結構化時間窗。"""

    __tablename__ = "rule_time_windows"
    __table_args__ = {"schema": "routing"}

    time_window_id = Column(UUID(as_uuid=True), primary_key=True)
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.restriction_rules.rule_id"),
        nullable=False,
    )
    day_type = Column(String(30), nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    month_mask = Column(String(50), nullable=True)
    exclude_holiday = Column(Boolean, nullable=False, server_default="false")
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
