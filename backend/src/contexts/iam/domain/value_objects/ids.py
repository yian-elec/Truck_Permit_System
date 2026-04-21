"""
ids.py — IAM 領域識別值物件

將 UUID 字串封裝為具驗證的型別，避免任意字串流入聚合，並讓方法簽名更具語意。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from ..errors import InvalidIamIdError


def _require_uuid_str(value: str, label: str) -> str:
    v = (value or "").strip()
    try:
        uuid.UUID(v)
    except ValueError as exc:
        raise InvalidIamIdError(f"{label} must be a valid UUID string") from exc
    return v


@dataclass(frozen=True)
class UserId:
    """使用者的唯一識別（對應 iam.users.user_id）。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_uuid_str(self.value, "UserId"))


@dataclass(frozen=True)
class RoleAssignmentId:
    """角色指派列的唯一識別（對應 iam.role_assignments.assignment_id）。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_uuid_str(self.value, "RoleAssignmentId"))


@dataclass(frozen=True)
class SessionId:
    """連線工作階段識別（對應 iam.sessions.session_id）。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_uuid_str(self.value, "SessionId"))


@dataclass(frozen=True)
class MfaChallengeId:
    """MFA 挑戰識別（對應 iam.mfa_challenges.challenge_id）。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_uuid_str(self.value, "MfaChallengeId"))
