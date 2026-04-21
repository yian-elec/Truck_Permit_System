"""
mfa_challenges — ORM 對應 iam.mfa_challenges。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class MfaChallenges(Base):
    """MFA 一次性驗證挑戰。"""

    __tablename__ = "mfa_challenges"
    __table_args__ = {"schema": "iam"}

    challenge_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("iam.users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    method = Column(String(30), nullable=False)
    target = Column(String(255), nullable=True)
    code_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
