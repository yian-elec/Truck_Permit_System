"""
applicant_profiles — ORM 對應 application.applicant_profiles。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class ApplicantProfiles(Base):
    """自然人申請人資料（一對一 application）。"""

    __tablename__ = "applicant_profiles"
    __table_args__ = {"schema": "application"}

    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.applications.application_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name = Column(String(100), nullable=False)
    id_no = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    mobile = Column(String(30), nullable=True)
    phone_area = Column(String(10), nullable=True)
    phone_no = Column(String(30), nullable=True)
    phone_ext = Column(String(10), nullable=True)
    address_county = Column(String(50), nullable=True)
    address_district = Column(String(50), nullable=True)
    address_detail = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
