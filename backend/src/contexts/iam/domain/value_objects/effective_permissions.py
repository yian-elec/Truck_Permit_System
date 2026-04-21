"""
effective_permissions.py — 有效權限集合值物件

對應 API「GET /auth/me/permissions」在領域中的結果型別：
由 App 依 iam.role_permissions 與使用者角色指派展開後，組裝為不可變集合傳入。
"""

from dataclasses import dataclass
from typing import FrozenSet

from .role_and_permission import PermissionCode


@dataclass(frozen=True)
class EffectivePermissionSet:
    """
    使用者在某時點的有效 PermissionCode 集合（唯讀快照）。

    責任：
    - 以 frozenset 表達不可變；不包含如何從資料庫 JOIN 的邏輯（屬 App／查詢層）。
    """

    codes: FrozenSet[PermissionCode]

    @classmethod
    def of(cls, *codes: PermissionCode) -> "EffectivePermissionSet":
        """由零或多個 PermissionCode 建立集合（重複代碼會因 frozenset 去重）。"""
        return cls(codes=frozenset(codes))

    def implies(self, required: PermissionCode) -> bool:
        """是否包含指定權限（供授權決策輔助，實際 gate 仍在 App 或政策引擎）。"""
        return required in self.codes
