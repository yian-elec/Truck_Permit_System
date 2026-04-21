"""
案件識別（Value Object，本 BC 之 surrogate identity）。

責任：在**不 import Application context** 的前提下，於 Page Model 領域中攜帶「指向某申請案件」的身分。
UUID 格式僅為便於與持久層／API path 對齊；相等性與驗證規則集中在此 VO。
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..errors import InvalidPageModelCompositionError


@dataclass(frozen=True)
class ApplicationSurrogateId:
    """
    申請案件 ID 在本 bounded context 中的值物件包裝。

    責任：確保聚合根（編輯器、審查頁）在領域上綁定單一案件；與他 context 的 `Application` 實體無型別耦合。
    """

    value: UUID

    def __post_init__(self) -> None:
        if self.value.int == 0:
            raise InvalidPageModelCompositionError(
                "ApplicationSurrogateId must not be the nil UUID"
            )
