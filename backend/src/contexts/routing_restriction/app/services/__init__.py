"""
Routing_Restriction 應用服務。

命名與責任切分（與 Application context 之 `*ApplicationService` 一致）：

- **RouteRequestApplicationService**：UC-ROUTE-01（路線申請、geocode、排程前置狀態）。
- **RoutePlanningApplicationService**：UC-ROUTE-02（候選產生、規則管線、持久化計畫樹）。
- **RoutePlanQueryApplicationService**：UC-ROUTE-03（最新計畫讀模型、規則命中列表）。
- **RoutePlanReviewApplicationService**：審查端寫入（UC-ROUTE-04 選線、UC-ROUTE-05 改線、replan），
  對應 6.4 **Review** 區塊之多支路由，仍屬「承辦對計畫之命令」單一邊界。
- **RestrictionAdminApplicationService**：Admin 規則 CRUD／啟停用、圖資列表與 publish。
- **MapImportApplicationService**：UC-ROUTE-06 匯入流程（目前埠未接時明確失敗）。
- **RoutingApplicationService**：Facade，供 API 單一注入點。

**services/ports/**：出站埠（Geocoding、RoutingProvider、SpatialRuleHit），由服務建構時注入，
實作可置換為 Infra Adapter，不與 HTTP 耦合。
"""

from . import ports
from .map_import_application_service import MapImportApplicationService
from .restriction_admin_application_service import RestrictionAdminApplicationService
from .route_plan_query_application_service import RoutePlanQueryApplicationService
from .route_plan_review_application_service import RoutePlanReviewApplicationService
from .route_planning_application_service import RoutePlanningApplicationService
from .route_request_application_service import RouteRequestApplicationService
from .routing_application_service import RoutingApplicationService

__all__ = [
    "MapImportApplicationService",
    "RestrictionAdminApplicationService",
    "RoutePlanQueryApplicationService",
    "RoutePlanReviewApplicationService",
    "RoutePlanningApplicationService",
    "RouteRequestApplicationService",
    "RoutingApplicationService",
    "ports",
]
