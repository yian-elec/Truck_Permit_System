"""
Routing_Restriction — Domain 層（DDD）。

責任：
- **聚合根**：`RouteRequest`（路線申請）、`RoutePlan`（規劃結果與候選集合）、`RestrictionRule`（限制規則定義）
- **實體**：`RouteCandidate`、`RouteSegment`（隸屬 `RoutePlan`）；`OfficerRouteOverride`（人工改線，以 application 關聯）
- **值物件**：座標、線段幾何、時段、車輛條件、規則命中、分數、版本語意等
- **領域服務**：`RestrictionEvaluationService`（候選路線規則檢核編排、forbidden／warning 優先、exception_road 覆蓋）
- **錯誤**：`routing_restriction.domain.errors`

依賴：僅標準函式庫與 `shared.errors.domain_error.DomainError`；**不**依賴 Infra、App、API。
"""

from .entities import (
    OfficerRouteOverride,
    RestrictionRule,
    RouteCandidate,
    RoutePlan,
    RouteRequest,
    RouteSegment,
)
from .errors import (
    CandidateNotInPlanError,
    GeocodingRequiredError,
    InvalidRoutePlanStateError,
    InvalidRouteRequestStateError,
    RoutingDomainError,
    RoutingInvalidValueError,
)
from .services import RestrictionEvaluationService, RoutingPipelinePolicy
from .value_objects import (
    EffectiveDateRange,
    GeoPoint,
    GeometryKind,
    HitSeverity,
    NoRouteExplanation,
    NoRouteReasonCode,
    RestrictionWindow,
    RouteGeometry,
    RoutePlanStatus,
    RouteRequestStatus,
    RouteScore,
    RuleHit,
    RuleType,
    RoutingDirection,
    VehicleConstraint,
)

__all__ = [
    # Aggregates / entities
    "RouteRequest",
    "RoutePlan",
    "RouteCandidate",
    "RouteSegment",
    "RestrictionRule",
    "OfficerRouteOverride",
    # Value objects
    "GeoPoint",
    "RouteGeometry",
    "GeometryKind",
    "RestrictionWindow",
    "EffectiveDateRange",
    "VehicleConstraint",
    "RuleHit",
    "RouteScore",
    "RuleType",
    "HitSeverity",
    "RouteRequestStatus",
    "RoutePlanStatus",
    "RoutingDirection",
    "NoRouteReasonCode",
    "NoRouteExplanation",
    # Services
    "RestrictionEvaluationService",
    "RoutingPipelinePolicy",
    # Errors
    "RoutingDomainError",
    "RoutingInvalidValueError",
    "InvalidRouteRequestStateError",
    "InvalidRoutePlanStateError",
    "CandidateNotInPlanError",
    "GeocodingRequiredError",
]
