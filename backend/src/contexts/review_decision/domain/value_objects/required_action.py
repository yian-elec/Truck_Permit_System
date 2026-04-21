"""
SupplementRequiredAction — 補件項目要求動作值物件。

責任：分類補件項目要求申請人執行之動作類型（對應 review.supplement_items.required_action），
供 UI 與驗證規則共用語彙。
"""

from __future__ import annotations

from enum import Enum


class SupplementRequiredAction(str, Enum):
    """
    補件項目之 required_action 枚舉。

    責任：以有限集合避免任意字串；實際代碼表可依產品擴充。
    """

    UPLOAD = "upload"
    """須上傳檔案。"""

    REPLACE = "replace"
    """須替換既有附件。"""

    CLARIFY = "clarify"
    """須澄清文字／欄位說明。"""

    RESUBMIT_ROUTE = "resubmit_route"
    """須重新提交路線（與 Routing context 銜接時由 App 解讀）。"""
