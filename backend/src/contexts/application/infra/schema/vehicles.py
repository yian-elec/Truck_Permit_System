"""
vehicles — ORM 對應 application.vehicles。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Numeric, String, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Vehicles(Base):
    """申請案件底下之車輛。"""

    __tablename__ = "vehicles"
    __table_args__ = {"schema": "application"}

    vehicle_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.applications.application_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plate_no = Column(String(20), nullable=False)
    vehicle_kind = Column(String(50), nullable=False)
    gross_weight_ton = Column(Numeric(8, 2), nullable=True)
    license_valid_until = Column(Date, nullable=True)
    trailer_plate_no = Column(String(20), nullable=True)
    is_primary = Column(Boolean, nullable=False, server_default=false(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
