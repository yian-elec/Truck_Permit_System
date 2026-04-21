"""
role_and_permission.py — 角色與權限代碼值物件

對應 iam.roles.role_code（varchar(50)）與 iam.permissions.permission_code（varchar(100)）；
權限展開（role → permissions）由 App 讀取對照表完成，領域僅保證代碼格式合理。
"""

from dataclasses import dataclass

from ..errors import InvalidIamCodeFormatError


def _non_empty_code(raw: str, label: str, max_len: int) -> str:
    v = (raw or "").strip()
    if not v:
        raise InvalidIamCodeFormatError(f"{label} must be non-empty")
    if len(v) > max_len:
        raise InvalidIamCodeFormatError(f"{label} exceeds maximum length")
    return v


@dataclass(frozen=True)
class RoleCode:
    """角色代碼（如審查員、系統管理員等），用於 RoleAssignment 與權限查詢鍵。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_code(self.value, "RoleCode", 50))


@dataclass(frozen=True)
class PermissionCode:
    """權限代碼；通常由角色—權限對照展開後供授權檢查使用。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_code(self.value, "PermissionCode", 100))
