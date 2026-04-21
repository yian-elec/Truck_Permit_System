"""
ocr_jobs — ORM 對應 ops.ocr_jobs。

檔名 {table_name}.py，類別名 OcrJobs（表名轉 PascalCase）。
"""

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class OcrJobs(Base):
    """OCR 作業主表（UC-OPS-01）。"""

    __tablename__ = "ocr_jobs"
    __table_args__ = {"schema": "ops"}

    ocr_job_id = Column(UUID(as_uuid=True), primary_key=True)
    attachment_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider_code = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
