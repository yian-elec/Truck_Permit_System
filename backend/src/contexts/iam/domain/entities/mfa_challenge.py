"""
mfa_challenge.py — MfaChallenge 聚合根

對應 iam.mfa_challenges：登入流程中若需 MFA，先建立 challenge，驗證碼比對由 App 呼叫
雜湊／驗證連接埠後，再呼叫領域方法標記完成。領域僅保存 code_hash，不處理明文 OTP。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..errors import (
    MfaChallengeAlreadyVerifiedError,
    MfaChallengeExpiredError,
    MfaChallengeInvariantViolationError,
)
from ..value_objects import MfaChallengeId, MfaMethod, UserId


@dataclass
class MfaChallenge:
    """
    MFA 挑戰聚合根。

    責任：
    - 保存挑戰識別、使用者、管道、目標（如手機／Email）與 code 雜湊、時效。
    - 控管「僅能驗證一次」與「過期不可驗證」規則（UC-IAM-03 領域側）。
    """

    challenge_id: MfaChallengeId
    user_id: UserId
    method: MfaMethod
    code_hash: str
    expires_at: datetime
    created_at: datetime
    target: Optional[str] = None
    verified_at: Optional[datetime] = None

    @staticmethod
    def issue(
        *,
        challenge_id: MfaChallengeId,
        user_id: UserId,
        method: MfaMethod,
        code_hash: str,
        expires_at: datetime,
        created_at: datetime,
        target: Optional[str] = None,
    ) -> MfaChallenge:
        """建立一筆待驗證的 MFA 挑戰（App 已產生雜湊與過期時間）。"""
        ch = (code_hash or "").strip()
        if not ch:
            raise MfaChallengeInvariantViolationError("code_hash is required")
        if expires_at <= created_at:
            raise MfaChallengeInvariantViolationError("expires_at must be after created_at")

        return MfaChallenge(
            challenge_id=challenge_id,
            user_id=user_id,
            method=method,
            target=_norm_optional(target),
            code_hash=ch,
            expires_at=expires_at,
            verified_at=None,
            created_at=created_at,
        )

    def assert_can_verify(self, now: datetime) -> None:
        """UC-IAM-03：驗證前檢查是否存在／未過期／尚未驗證過。"""
        if self.verified_at is not None:
            raise MfaChallengeAlreadyVerifiedError("MFA challenge already verified")
        if now >= self.expires_at:
            raise MfaChallengeExpiredError("MFA challenge has expired")

    def complete_verification(self, now: datetime) -> None:
        """
        在 App 層已比對 OTP 與 code_hash 成立後呼叫，標記 verified_at。

        應先呼叫 assert_can_verify(now)。
        """
        self.assert_can_verify(now)
        self.verified_at = now


def _norm_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = value.strip()
    return s if s else None
