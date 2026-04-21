"""
role_assignment.py — 角色指派實體

隸屬於 User 聚合：描述某使用者在某範圍下擁有的角色。
由 User 聚合根維護不變條件（承辦／管理者至少一筆指派）。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import AssignmentScope, RoleAssignmentId, RoleCode, UserId


@dataclass
class RoleAssignment:
    """
    角色指派實體（非聚合根）。

    責任：
    - 保存 assignment_id、所屬 user、角色代碼與可選範圍。
    - 與資料表 iam.role_assignments 語意對齊；生命週期由 User 聚合根管理。
    """

    assignment_id: RoleAssignmentId
    user_id: UserId
    role_code: RoleCode
    created_at: datetime
    updated_at: datetime
    scope: AssignmentScope = field(default_factory=lambda: AssignmentScope())

    def same_binding(self, role_code: RoleCode, scope: AssignmentScope) -> bool:
        """是否與另一個「角色 + 範圍」組合指涉同一條指派業務鍵（用於 upsert）。"""
        return self.role_code.value == role_code.value and self._scope_key() == scope_key(scope)

    def touch_updated(self, now: datetime) -> None:
        """更新業務上的修改時間（由聚合根在變更後呼叫）。"""
        self.updated_at = now

    def _scope_key(self) -> tuple[Optional[str], Optional[str]]:
        return (self.scope.scope_type, self.scope.scope_id)


def scope_key(scope: AssignmentScope) -> tuple[Optional[str], Optional[str]]:
    return (scope.scope_type, scope.scope_id)
