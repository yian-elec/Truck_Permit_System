"""
ReviewStage — 審查階段值物件。

責任：以有限集合表達案件在審查管線中的階段（對應 review.review_tasks.stage），
避免任意字串流入領域；供 ReviewTask 持有並與規格 varchar(30) 對齊。
"""

from __future__ import annotations

from enum import Enum


class ReviewStage(str, Enum):
    """
    審查階段枚舉。

    責任：與 Infra 層儲存之 stage 字串一一對應；新增階段時應同步 migration 與 App 用例。
    """

    INITIAL = "initial"
    """首次審查（建立任務後預設階段範例，實際代碼可依專案詞彙調整）。"""

    SECOND_LINE = "second_line"
    """二線／複核階段（範例）。"""

    FINAL = "final"
    """終審階段（範例）。"""
