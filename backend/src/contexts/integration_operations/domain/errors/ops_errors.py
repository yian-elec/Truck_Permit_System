"""
Integration_Operations context 專屬領域錯誤。

責任：表達作業協調（OCR、通知、稽核、匯入）過程中違反不變條件或狀態機的情況。
僅依賴 shared 的 DomainError 基底，不依賴 Infra / App / API。
"""

from typing import Any, Dict, Optional

from shared.errors.domain_error import DomainError


class OpsDomainError(DomainError):
    """
    Integration_Operations 領域錯誤基底。

    用途：統一此 context 內所有業務規則違例的父類型，便於 App 層捕捉與對應處理。
    """

    pass


class InvalidJobStateError(OpsDomainError):
    """
    作業狀態不允許執行所請求的領域行為。

    用途：例如於已結束的 OCR Job 上再次呼叫 start，或於已送達的通知上標記失敗。
    """

    def __init__(
        self,
        message: str,
        *,
        current_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        d = dict(details or {})
        if current_status is not None:
            d["current_status"] = current_status
        super().__init__(message, d if d else None)


class InvalidDomainValueError(OpsDomainError):
    """
    值物件或欄位格式／範圍不符合領域約束。

    用途：Provider 代碼過長、信心分數超出 [0,1]、必填 payload 為空等。
    """

    pass
