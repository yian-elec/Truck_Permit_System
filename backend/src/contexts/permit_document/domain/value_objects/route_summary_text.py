"""
RouteSummaryText — 正式路線摘錄文字值物件。

責任：封裝 `route_summary_text text not null` 之領域意義（對外公開、可列印於許可證上之摘錄），
確保非空白；實際由 segments 組字串的演算法屬 App 層，Domain 只驗證結果文字之合法性。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.permit_document.domain.errors import InvalidPermitValueError

# 合理上限，避免異常大段文字進入聚合（與 DB text 無硬上限之間的護欄）
_MAX_CHARS = 200_000


@dataclass(frozen=True)
class RouteSummaryText:
    """
    綁定於許可之最終路線說明文字（不可變）。

    責任：trim 後必須非空，長度不超過政策上限。
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidPermitValueError("RouteSummaryText must not be empty")
        if len(normalized) > _MAX_CHARS:
            raise InvalidPermitValueError(
                f"RouteSummaryText exceeds max length {_MAX_CHARS}"
            )
        object.__setattr__(self, "value", normalized)
