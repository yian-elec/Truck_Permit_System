"""
scope.py — 角色指派範圍值物件

對應 iam.role_assignments.scope_type / scope_id：
權限可依行政區、單位等範圍限縮；兩欄必須同時為空或同時有值。
"""

from dataclasses import dataclass
from typing import Optional

from ..errors import InvalidAssignmentScopePairError


@dataclass(frozen=True)
class AssignmentScope:
    """
    角色指派的範圍（可選）。
    None + None 表示全域該角色；否則兩者皆須提供。
    """

    scope_type: Optional[str] = None
    scope_id: Optional[str] = None

    def __post_init__(self) -> None:
        st = self._norm(self.scope_type)
        sid = self._norm(self.scope_id)
        if (st is None) ^ (sid is None):
            raise InvalidAssignmentScopePairError(
                "scope_type and scope_id must both be set or both be empty"
            )
        object.__setattr__(self, "scope_type", st)
        object.__setattr__(self, "scope_id", sid)

    @staticmethod
    def _norm(x: Optional[str]) -> Optional[str]:
        if x is None:
            return None
        s = x.strip()
        return s if s else None

    def is_global(self) -> bool:
        return self.scope_type is None and self.scope_id is None
