"""
permits — ORM 對應 permit.permits。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Permits(Base):
    """許可證主表（對應領域 Permit 聚合持久化列）。"""

    __tablename__ = "permits"
    __table_args__ = (
        UniqueConstraint("application_id", name="uq_permits_application_id"),
        {"schema": "permit"},
    )

    permit_id = Column(UUID(as_uuid=True), primary_key=True)
    permit_no = Column(String(30), unique=True, nullable=False)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(30), nullable=False)
    approved_start_at = Column(DateTime(timezone=True), nullable=False)
    approved_end_at = Column(DateTime(timezone=True), nullable=False)
    selected_candidate_id = Column(UUID(as_uuid=True), nullable=True)
    override_id = Column(UUID(as_uuid=True), nullable=True)
    route_summary_text = Column(Text, nullable=False)
    note = Column(Text, nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    issued_by = Column(UUID(as_uuid=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)
    revoked_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
