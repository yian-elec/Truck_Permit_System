"""
Review_Decision bounded context — Domain 層公開介面。

責任：匯出聚合根、值物件、領域服務與錯誤型別，供 App 層編排用例；本套件不依賴 Infra/App/API。
"""

from src.contexts.review_decision.domain.entities import (
    ReviewDecision,
    ReviewTask,
    SupplementRequest,
)
from src.contexts.review_decision.domain.errors import (
    InvalidReviewTaskStateError,
    InvalidSupplementRequestStateError,
    ReviewDecisionConflictError,
    ReviewDecisionRuleError,
    ReviewDomainError,
    ReviewInvalidValueError,
)
from src.contexts.review_decision.domain.services import ReviewWorkflowPolicy
from src.contexts.review_decision.domain.value_objects import (
    ApprovalRouteReadiness,
    ApprovedPeriod,
    CommentType,
    DecisionType,
    ReviewComment,
    ReviewStage,
    ReviewTaskStatus,
    SupplementItem,
    SupplementRequestStatus,
    SupplementRequiredAction,
)

__all__ = [
    # Aggregates
    "ReviewTask",
    "ReviewDecision",
    "SupplementRequest",
    # Value objects
    "ReviewStage",
    "DecisionType",
    "CommentType",
    "ReviewTaskStatus",
    "SupplementRequestStatus",
    "SupplementRequiredAction",
    "SupplementItem",
    "ReviewComment",
    "ApprovedPeriod",
    "ApprovalRouteReadiness",
    # Domain service
    "ReviewWorkflowPolicy",
    # Errors
    "ReviewDomainError",
    "ReviewInvalidValueError",
    "InvalidReviewTaskStateError",
    "ReviewDecisionRuleError",
    "ReviewDecisionConflictError",
    "InvalidSupplementRequestStateError",
]
