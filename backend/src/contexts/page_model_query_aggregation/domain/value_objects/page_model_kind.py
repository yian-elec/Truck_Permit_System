"""
Page Model 種類（Value Object）。

責任：對應規格中的四條 Page Model API 路徑語意，使領域規則能以型別安全方式分支，
而非散佈魔法字串。與 HTTP path 的對應由 App 層負責，本 VO 僅表達領域分類。
"""

from __future__ import annotations

from enum import StrEnum


class PageModelKind(StrEnum):
    """
    畫面專用聚合 read model 的領域分類。

    責任：標記「哪一種 Page Model 契約」正在被組裝，供聚合根與 Domain Service 選擇區塊目錄與不變條件。
    """

    APPLICANT_APPLICATION_HOME = "applicant_application_home"
    """申請人入口／首頁模型（對應 GET …/application-home-model）。"""

    APPLICANT_APPLICATION_EDITOR = "applicant_application_editor"
    """申請人單一案件編輯器模型（對應 GET …/applications/{id}/editor-model）。"""

    REVIEW_APPLICATION = "review_application"
    """審查員單一案件審查模型（對應 GET …/review-model）。"""

    ADMIN_DASHBOARD = "admin_dashboard"
    """管理者儀表板模型（對應 GET …/dashboard-model）。"""
