"""
session_expiry — 登入／refresh 時計算 iam.sessions.expires_at。

當同時簽發 refresh 時，工作階段存活時間應涵蓋 refresh TTL，否則 access 過期後無法 refresh。
"""

from __future__ import annotations

from datetime import datetime, timedelta


def compute_session_expires_at(
    now: datetime,
    *,
    access_ttl_seconds: int,
    refresh_jti: str | None,
    refresh_ttl_seconds: int | None,
) -> datetime:
    access_expires = now + timedelta(seconds=access_ttl_seconds)
    if refresh_jti and refresh_ttl_seconds is not None and refresh_ttl_seconds > 0:
        refresh_expires = now + timedelta(seconds=refresh_ttl_seconds)
        return max(access_expires, refresh_expires)
    return access_expires
