"""
registration_notifier_port — UC-IAM-01 註冊後驗證／通知（政策開關）。
"""

from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID


class RegistrationNotifierPort(Protocol):
    def send_registration_verification_notice(
        self,
        *,
        user_id: UUID,
        display_name: str,
        email: Optional[str],
        mobile: Optional[str],
    ) -> None:
        """視產品政策寄送 Email／簡訊或僅記錄；不得拋出致註冊失敗（由實作保證）。"""
        ...


class NoopRegistrationNotifierPort:
    """預設不發送。"""

    def send_registration_verification_notice(
        self,
        *,
        user_id: UUID,
        display_name: str,
        email: Optional[str],
        mobile: Optional[str],
    ) -> None:
        return None
