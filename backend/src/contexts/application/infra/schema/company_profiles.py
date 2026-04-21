"""
company_profiles — ORM 對應 application.company_profiles。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class CompanyProfiles(Base):
    """公司申請人資料（一對一 application）。"""

    __tablename__ = "company_profiles"
    __table_args__ = {"schema": "application"}

    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.applications.application_id", ondelete="CASCADE"),
        primary_key=True,
    )
    company_name = Column(String(255), nullable=True)
    tax_id = Column(String(20), nullable=True)
    principal_name = Column(String(100), nullable=True)
    contact_name = Column(String(100), nullable=True)
    contact_mobile = Column(String(30), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
