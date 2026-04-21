"""
Application API 依賴注入。

責任：提供 `ApplicationCommandService`、`PublicHeavyTruckPermitService` 與 JWT `sub` → `applicant_user_id`（UUID）
之解析；路由層僅宣告 Depends，不實作業務邏輯。
"""

from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import Request

from src.contexts.application.app.services import ApplicationCommandService
from src.contexts.application.infra.repositories import ApplicationReadModelQueryImpl
from src.contexts.application.infra.review_supplement_workflow_adapter import (
    ReviewSupplementWorkflowAdapter,
)
from shared.errors.system_error.auth_error import MissingTokenError


def applicant_user_uuid_from_jwt_sub(sub: object | None) -> UUID:
    """
    將 JWT `sub` 轉為申請案件所使用之 `applicant_user_id`（UUID）。

    責任：若 `sub` 已是合法 UUID 字串則直接使用；否則以穩定命名空間 UUID 由字串衍生，
    使同一登入帳號始終對應同一申請人識別（直至改為帳號表存放真實 UUID）。
    """
    if sub is None:
        raise MissingTokenError("Token 缺少使用者主體（sub）")
    s = str(sub).strip()
    try:
        return UUID(s)
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"truck-permit-applicant:{s}")


def get_applicant_user_id(request: Request) -> UUID:
    """從已通過認證中介軟體之 `request.state.user` 取得申請人 UUID。"""
    user = getattr(request.state, "user", None)
    if not user:
        raise MissingTokenError("未授權：缺少使用者資訊")
    return applicant_user_uuid_from_jwt_sub(user.get("user_id"))


def get_application_command_service() -> ApplicationCommandService:
    """建立申請案件命令服務實例（讀模型：列表與附件摘要等，送件不檢查路線申請列）。"""
    return ApplicationCommandService(
        read_model=ApplicationReadModelQueryImpl(),
        supplement_workflow=ReviewSupplementWorkflowAdapter(),
    )
