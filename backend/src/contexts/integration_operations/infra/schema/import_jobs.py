"""
import_jobs — ORM 對應 ops.import_jobs。
"""

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class ImportJobs(Base):
    """外部資料匯入作業（UC-OPS-04）。"""

    __tablename__ = "import_jobs"
    __table_args__ = {"schema": "ops"}

    import_job_id = Column(UUID(as_uuid=True), primary_key=True)
    job_type = Column(String(50), nullable=False)
    source_name = Column(String(100), nullable=False)
    source_ref = Column(String(255), nullable=True)
    status = Column(String(30), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    result_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
