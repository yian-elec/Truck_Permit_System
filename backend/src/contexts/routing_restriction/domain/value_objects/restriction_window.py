"""
RestrictionWindow — 規則適用之時間窗（值物件）。

責任：對應結構化後之時段條件（平日／假日、起迄時刻、月份遮罩、是否排除國定假日等），
供領域判斷「申請出發時間」是否落入禁行時段；保留 `raw_text` 以對應未完全解析之原文。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass(frozen=True)
class RestrictionWindow:
    """
    單一規則之時間維度約束。

    責任：
    - **day_type**：如 all / weekday / weekend / custom（字串由匯入與政策約定，領域僅保存與比對）。
    - **start_time / end_time**：可為空表示全日或依 day_type 解讀。
    - **month_mask**：可選，如 "1-3,11-12" 由 App/Infra 預先正規化或於服務內解讀。
    - **exclude_holiday**：為 True 時應排除國定假日（實際假日曆在 App 注入或查詢埠，本 VO 只攜帶旗標）。
    - **raw_text**：對應 KML description 原文片段，供稽核。
    """

    day_type: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    month_mask: Optional[str] = None
    exclude_holiday: bool = False
    raw_text: Optional[str] = None

    def applies_at(
        self,
        departure: datetime,
        *,
        is_public_holiday: bool,
    ) -> bool:
        """
        判斷此時間窗於出發時刻是否「生效」（與禁行／限制時段比對）。

        責任：
        - **exclude_holiday**：為 True 且 `is_public_holiday` 為 True 時，本窗不生效（不構成限制）。
        - **day_type**：辨識 all／平日／假日等（匯入層應正規化小寫；未知字串採保守策略視為需再檢查時段）。
        - **start_time / end_time**：皆空視為全日；支援跨日窗（end < start 表示跨越午夜）。

        不負責：月份遮罩 **month_mask** 的複雜解析（仍須由匯入或 App 預處理或後續擴充）。
        """
        if self.exclude_holiday and is_public_holiday:
            return False

        wd = departure.weekday()  # 0=Mon .. 6=Sun
        clock = departure.time()
        dtype = (self.day_type or "").strip().lower()

        if dtype in ("weekday", "平日", "平"):
            if wd >= 5:
                return False
        elif dtype in ("weekend", "假日", "例假日", "週末"):
            if wd < 5:
                return False
        elif dtype not in (
            "",
            "all",
            "daily",
            "全日",
            "any",
            "always",
        ):
            # custom 或其他：在未解析前仍檢查時段，避免 silent 放寬
            pass

        if self.start_time is None and self.end_time is None:
            return True
        if self.start_time is not None and self.end_time is not None:
            if self.start_time <= self.end_time:
                return self.start_time <= clock <= self.end_time
            return clock >= self.start_time or clock <= self.end_time
        if self.start_time is not None:
            return clock >= self.start_time
        if self.end_time is not None:
            return clock <= self.end_time
        return True
