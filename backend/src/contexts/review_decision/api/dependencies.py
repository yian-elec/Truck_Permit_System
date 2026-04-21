"""
Review_Decision API 依賴注入。

責任：組裝 `ReviewServiceContext` 與 Command/Query 服務，並與 `ApplicationCommandService`
共用同一 `ApplicationRepositoryImpl` 實例；JWT 承辦人 UUID 解析與申請人 API 相同語意。
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Request

from src.contexts.application.api.dependencies import applicant_user_uuid_from_jwt_sub
from src.contexts.application.app.services import ApplicationCommandService
from src.contexts.application.app.services.application_query_service import ApplicationQueryService
from src.contexts.application.app.services.application_service_context import ApplicationServiceContext
from src.contexts.application.app.services._policy import DEFAULT_MAX_PERMIT_CALENDAR_DAYS
from src.contexts.application.app.services.ports.outbound import (
    NoopApplicationEventPublisher,
    NoopFileStoragePort,
    NoopSupplementWorkflowPort,
)
from src.contexts.application.infra.repositories import (
    ApplicationReadModelQueryImpl,
    ApplicationRepositoryImpl,
)
from src.contexts.review_decision.app.services import (
    ReviewCommandApplicationService,
    ReviewQueryApplicationService,
    ReviewServiceContext,
)
from src.contexts.review_decision.app.services.ports.outbound import NoopReviewNotificationPort
from src.contexts.review_decision.infra.repositories import (
    DecisionsRepository,
    ReviewCommentsRepository,
    ReviewTasksRepository,
    SupplementRequestsRepository,
)
from src.contexts.routing_restriction.app.services.route_plan_query_application_service import (
    RoutePlanQueryApplicationService,
)
from shared.errors.system_error.auth_error import MissingTokenError


def get_officer_user_id(request: Request) -> UUID:
    """
    從 JWT 解析承辦／審查人員 UUID（與 `get_applicant_user_id` 相同之 `sub` 映射規則）。

    責任：實際角色檢查由授權政策擴充；此處僅保證已登入使用者識別。
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise MissingTokenError("未授權：缺少使用者資訊")
    return applicant_user_uuid_from_jwt_sub(user.get("user_id"))


@dataclass
class ReviewApiBundle:
    """單一請求內共用之審查命令／查詢與申請案件命令服務。"""

    r_cmd: ReviewCommandApplicationService
    r_q: ReviewQueryApplicationService
    app_cmd: ApplicationCommandService


def get_review_api_bundle() -> ReviewApiBundle:
    """
    建立審查 API 用依賴組（每個請求新建，確保儲存庫實例一致）。

    責任：與 `get_application_command_service` 共用讀模型（列表／附件摘要等）；
    事件／審查通知預設為 Noop，正式環境可改為注入真實 Outbox／通知埠。
    """
    repo = ApplicationRepositoryImpl()
    read = ApplicationReadModelQueryImpl()
    submission_events = NoopApplicationEventPublisher()
    app_cmd = ApplicationCommandService(
        repository=repo,
        read_model=read,
        event_publisher=submission_events,
    )
    app_ctx = ApplicationServiceContext(
        repository=repo,
        read_model=read,
        file_storage=NoopFileStoragePort(),
        event_publisher=submission_events,
        supplement_workflow=NoopSupplementWorkflowPort(),
        max_permit_calendar_days=DEFAULT_MAX_PERMIT_CALENDAR_DAYS,
    )
    app_query = ApplicationQueryService(app_ctx)
    r_ctx = ReviewServiceContext(
        tasks=ReviewTasksRepository(),
        decisions=DecisionsRepository(),
        comments=ReviewCommentsRepository(),
        supplements=SupplementRequestsRepository(),
        applications=repo,
        application_queries=app_query,
        route_plans=RoutePlanQueryApplicationService(),
        events=NoopApplicationEventPublisher(),
        notifications=NoopReviewNotificationPort(),
    )
    return ReviewApiBundle(
        r_cmd=ReviewCommandApplicationService(r_ctx),
        r_q=ReviewQueryApplicationService(r_ctx),
        app_cmd=app_cmd,
    )
