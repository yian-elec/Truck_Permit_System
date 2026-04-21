"""
notification_jobs — ORM 對應 ops.notification_jobs。
"""

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class NotificationJobs(Base):
    """通知作業（UC-OPS-02）。"""

    __tablename__ = "notification_jobs"
    __table_args__ = {"schema": "ops"}

    notification_job_id = Column(UUID(as_uuid=True), primary_key=True)
    channel = Column(String(30), nullable=False)
    recipient = Column(String(255), nullable=False)
    template_code = Column(String(50), nullable=False)
    payload_json = Column(JSONB, nullable=False)
    status = Column(String(30), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
