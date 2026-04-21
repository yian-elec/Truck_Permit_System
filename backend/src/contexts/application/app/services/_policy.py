"""
申請案件相關政策常數（App 層）。

責任：將「許可期間最長曆日數」等可由監理機關調整之參數集中；領域仍由參數注入驗證。
"""

from __future__ import annotations

# 預設：申請人請求之通行期間不得超過之曆日上限（含起訖日）
DEFAULT_MAX_PERMIT_CALENDAR_DAYS: int = 366
