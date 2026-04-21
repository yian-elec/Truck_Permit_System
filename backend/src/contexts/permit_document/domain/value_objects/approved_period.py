"""
PermitApprovedPeriod — 許可證上之核准有效期間值物件。

責任：對應 schema `approved_start_at` / `approved_end_at` 皆 **NOT NULL** 之約束，
封裝起訖有序（起 < 訖）之不變條件；與 Review_Decision 之 ApprovedPeriod 語意對齊但 **不匯入** 該 context，
以維持 Permit_Document bounded context 之邊界與獨立演進。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.contexts.permit_document.domain.errors import InvalidPermitValueError


@dataclass(frozen=True)
class PermitApprovedPeriod:
    """
    核准後寫入許可證之通行期間（牆上時鐘，建議 aware UTC）。

    責任：兩端皆必填，且 **start_at 必須嚴格早於 end_at**（與「僅核准案可建證」搭配，
    期間來源為核准決策，由 App 層讀取後傳入）。
    """

    start_at: datetime
    end_at: datetime

    def __post_init__(self) -> None:
        if self.start_at >= self.end_at:
            raise InvalidPermitValueError(
                "PermitApprovedPeriod requires start_at strictly before end_at"
            )
