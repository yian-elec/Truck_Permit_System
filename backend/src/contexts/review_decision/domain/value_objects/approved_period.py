"""
ApprovedPeriod — 核准有效期間值物件。

責任：封裝 approved_start_at／approved_end_at 之領域不變條件（起訖有序、可為開放式邊界之政策由參數表達）；
供 ReviewDecision 核准時持有。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.contexts.review_decision.domain.errors import ReviewInvalidValueError


@dataclass(frozen=True)
class ApprovedPeriod:
    """
    核准許可期間。

    責任：
    - 若兩端皆提供，必須滿足 **start <= end**（時區由呼叫端統一為 UTC 或帶 tz 之 datetime）。
    - 允許僅一端為 None 的情況由產品決定；本類別僅在兩者皆存在時檢查順序。
    """

    start_at: datetime | None
    end_at: datetime | None

    def __post_init__(self) -> None:
        if self.start_at is not None and self.end_at is not None:
            if self.start_at > self.end_at:
                raise ReviewInvalidValueError(
                    "approved_start_at must not be after approved_end_at"
                )
