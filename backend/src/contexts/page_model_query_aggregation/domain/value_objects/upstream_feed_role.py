"""
上游資料來源角色（Value Object / 枚舉）。

責任：以**語意標籤**標示「某區塊的資料應由哪一類上游 bounded context 餵入」，
供 App 層對應到實際的 Application Service／Repository，**不在此處** import 那些 context。
同一角色可能對應多個 HTTP 或內部查詢，屬整合細節，非本領域關心範圍。
"""

from __future__ import annotations

from enum import StrEnum


class UpstreamFeedRole(StrEnum):
    """
    區塊資料來源的領域角色（與 Identity_Access、Application 等 context 概念對齊，但無程式依賴）。

    責任：讓 Page Model 組版規則能陳述「需要哪類資料」而不綁定具體 API。
    """

    PUBLIC_SERVICE_COPY = "public_service_copy"
    """公開服務說明、必備文件、條款摘要等靜態／準靜態文案（對應 Application 公開 read）。"""

    USER_ACCOUNT_SUMMARY = "user_account_summary"
    """目前登入使用者之帳號摘要（對應 Identity_Access）。"""

    MY_APPLICATIONS_SUMMARY = "my_applications_summary"
    """申請人名下案件列表／摘要（對應 Application 查詢；語意與單一案件核心區塊不同）。"""

    APPLICATION_CASE_CORE = "application_case_core"
    """單一案件主檔與狀態時間軸等核心欄位（對應 Application）。"""

    APPLICATION_VEHICLES = "application_vehicles"
    """案件綁定車輛列表（對應 Application）。"""

    APPLICATION_ATTACHMENTS = "application_attachments"
    """附件、上傳狀態、檢核項目（對應 Application）。"""

    ROUTING_REQUEST_AND_PLANS = "routing_request_and_plans"
    """路徑申請、方案、禁限規則命中等（對應 Routing_Restriction）。"""

    REVIEW_TASKS_AND_DECISIONS = "review_tasks_and_decisions"
    """審查任務、補件、決定與評論（對應 Review_Decision）。"""

    PERMIT_DOCUMENTS = "permit_documents"
    """許可證與文件產製狀態（對應 Permit_Document）。"""

    OPS_ACTIVITY_FEED = "ops_activity_feed"
    """OCR／通知／匯入等作業摘要或列表（對應 Integration_Operations）。"""

    ADMIN_METRICS_AGGREGATE = "admin_metrics_aggregate"
    """管理者儀表板用匯總指標占位（可由多 context 匯總，App 層實作）。"""
