"""
audit_logs — ORM 對應 ops.audit_logs。
"""

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class AuditLogs(Base):
    """稽核紀錄（UC-OPS-03）。"""

    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "ops"}

    audit_log_id = Column(UUID(as_uuid=True), primary_key=True)
    actor_user_id = Column(UUID(as_uuid=True), nullable=True)
    actor_type = Column(String(30), nullable=False)
    action_code = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    before_json = Column(JSONB, nullable=True)
    after_json = Column(JSONB, nullable=True)
    client_ip = Column(INET, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
