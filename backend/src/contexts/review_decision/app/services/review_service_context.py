"""
Review 用例服務共用依賴（儲存庫、跨 context 查詢、事件／通知埠）。

責任：由組合根（例如 FastAPI lifespan 或測試 fixture）建構並注入各 Command/Query 服務，
避免服務內直接 new 具體 Infra 實作。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.application.app.services.application_query_service import (
    ApplicationQueryService,
)
from src.contexts.application.app.services.ports.outbound import ApplicationEventPublisher
from src.contexts.application.infra.repositories import ApplicationRepositoryImpl
from src.contexts.review_decision.app.services.ports.outbound import ReviewNotificationPort
from src.contexts.review_decision.infra.repositories import (
    DecisionsRepository,
    ReviewCommentsRepository,
    ReviewTasksRepository,
    SupplementRequestsRepository,
)
from src.contexts.routing_restriction.app.services.route_plan_query_application_service import (
    RoutePlanQueryApplicationService,
)


@dataclass
class ReviewServiceContext:
    """
    審查決策用例執行上下文。

    責任：持有 review schema 儲存庫、案件讀寫、路線唯讀查詢與事件／通知埠。
    """

    tasks: ReviewTasksRepository
    decisions: DecisionsRepository
    comments: ReviewCommentsRepository
    supplements: SupplementRequestsRepository
    applications: ApplicationRepositoryImpl
    application_queries: ApplicationQueryService
    route_plans: RoutePlanQueryApplicationService
    events: ApplicationEventPublisher
    notifications: ReviewNotificationPort
