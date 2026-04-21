"""
ocr_results — ORM 對應 ops.ocr_results。

與 ocr_jobs 以 attachment_id 語意關聯（規格未含 ocr_job_id FK）。
"""

from sqlalchemy import Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class OcrResults(Base):
    """OCR 欄位級辨識結果。"""

    __tablename__ = "ocr_results"
    __table_args__ = {"schema": "ops"}

    ocr_result_id = Column(UUID(as_uuid=True), primary_key=True)
    attachment_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    raw_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
