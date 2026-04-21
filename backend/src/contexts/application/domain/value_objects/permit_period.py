"""
許可申請期間（Value Object）。

責任：封裝 requested_start_at／requested_end_at 的不變條件（起訖有序、不可為空），
並提供「不得超過政策上限天數」之驗證，供 UC 與 Aggregate 送件前檢查呼叫。
政策天數由呼叫端注入，維持 Domain 不依賴設定檔或 DB。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ..errors import InvalidDomainValueError


@dataclass(frozen=True)
class PermitPeriod:
    """
    申請人請求之通行許可期間（牆上時鐘時間，建議為 aware UTC）。

    責任：確保 end > start；與「政策允許最長天數」的檢查分離為方法，便於單元測試與重用。
    """

    start_at: datetime
    end_at: datetime

    def __post_init__(self) -> None:
        if self.start_at >= self.end_at:
            raise InvalidDomainValueError(
                "Permit period requires start_at strictly before end_at",
            )

    def duration_days_inclusive(self) -> int:
        """
        以日曆日估算涵蓋天數（含起訖日），供政策上限比對。

        責任：採 date 差異 +1；若需更細粒度（時分）政策，可於 App 層換算後傳入 max_days。
        """
        start_d = self.start_at.date()
        end_d = self.end_at.date()
        return (end_d - start_d).days + 1

    def assert_within_max_calendar_days(self, max_calendar_days: int) -> None:
        """
        驗證申請期間不得超過政策允許之上限（以曆日數計）。

        責任：對應「申請期間不得超過政策上限」；max_calendar_days 須 > 0，由政策模組傳入。
        """
        if max_calendar_days < 1:
            raise InvalidDomainValueError("max_calendar_days must be at least 1")
        actual = self.duration_days_inclusive()
        if actual > max_calendar_days:
            raise InvalidDomainValueError(
                f"Permit period spans {actual} calendar days; "
                f"exceeds policy maximum of {max_calendar_days}",
            )


def ensure_utc_aware(dt: datetime) -> datetime:
    """
    將 naive datetime 視為 UTC 並加上 tzinfo（純領域輔助，可選用）。

    責任：避免 ORM／API 傳入 naive 導致比較歧義；若專案一律使用 aware，可不在此呼叫。
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
