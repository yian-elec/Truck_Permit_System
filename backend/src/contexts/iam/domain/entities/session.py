"""
session.py — Session 聚合根

對應 Aggregate「Session」與 iam.sessions：記錄一次登入後簽發的 token 與工作階段生命週期。
與 User 分開成獨立聚合，避免高頻 token 刷新鎖住整個 User 聚合。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..errors import SessionInvariantViolationError, SessionNotActiveError
from ..value_objects import SessionId, UserId


@dataclass
class Session:
    """
    Session 聚合根。

    責任：
    - 保存 access／refresh token 的 JTI 與過期、撤銷時間。
    - 提供撤銷與「在某一時點是否仍有效」的判斷，供 App 層實作 logout／refresh 規則。
    """

    session_id: SessionId
    user_id: UserId
    access_token_jti: str
    expires_at: datetime
    issued_at: datetime
    created_at: datetime
    refresh_token_jti: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None

    @staticmethod
    def open_session(
        *,
        session_id: SessionId,
        user_id: UserId,
        access_token_jti: str,
        refresh_token_jti: Optional[str],
        issued_at: datetime,
        expires_at: datetime,
        created_at: datetime,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session:
        """建立一筆新的有效 Session（登入或 MFA 驗證成功後由 App 呼叫）。"""
        aj = (access_token_jti or "").strip()
        if not aj:
            raise SessionInvariantViolationError("access_token_jti is required")
        if expires_at <= issued_at:
            raise SessionInvariantViolationError("expires_at must be after issued_at")

        return Session(
            session_id=session_id,
            user_id=user_id,
            access_token_jti=aj,
            refresh_token_jti=_norm_jti(refresh_token_jti),
            client_ip=_norm_optional(client_ip),
            user_agent=_norm_optional(user_agent),
            issued_at=issued_at,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None,
        )

    def revoke(self, now: datetime) -> None:
        """登出或強制失效時標記 revoked_at。"""
        if self.revoked_at is None:
            self.revoked_at = now

    def assert_active_at(self, now: datetime) -> None:
        """若已撤銷或已過期則拋錯，供 refresh 或敏感操作前使用。"""
        if self.revoked_at is not None:
            raise SessionNotActiveError("Session has been revoked")
        if now >= self.expires_at:
            raise SessionNotActiveError("Session has expired")

    def is_active_at(self, now: datetime) -> bool:
        """僅供查詢；不拋錯。"""
        try:
            self.assert_active_at(now)
            return True
        except SessionNotActiveError:
            return False


def _norm_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = value.strip()
    return s if s else None


def _norm_jti(value: Optional[str]) -> Optional[str]:
    return _norm_optional(value)
