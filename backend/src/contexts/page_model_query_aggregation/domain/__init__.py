"""
Page Model Query Aggregation — Domain 層。

責任：表達 Page Model 的區塊契約、聚合邊界與組版規則；不依賴 Infra、App、API 或其他 bounded context 的實作類型。
"""

from .errors import (
    DuplicateSectionOrderError,
    InvalidPageModelCompositionError,
    PageModelDomainError,
    PrerequisiteSectionMissingError,
    UnknownSectionCodeError,
)
from .value_objects import (
    ApplicationLifecycleSnapshot,
    ApplicationLifecyclePhase,
    ApplicationSurrogateId,
    ModelContractVersion,
    PageModelKind,
    PageSectionCode,
    UpstreamFeedRole,
)
from .entities import (
    AdminDashboardPageModel,
    ApplicantApplicationEditorPageModel,
    ApplicantApplicationHomePageModel,
    PageModelSectionSpec,
    ReviewApplicationPageModel,
)
from .services import PageModelSectionCatalog

__all__ = [
    "PageModelDomainError",
    "InvalidPageModelCompositionError",
    "UnknownSectionCodeError",
    "DuplicateSectionOrderError",
    "PrerequisiteSectionMissingError",
    "PageModelKind",
    "PageSectionCode",
    "UpstreamFeedRole",
    "ApplicationSurrogateId",
    "ApplicationLifecyclePhase",
    "ApplicationLifecycleSnapshot",
    "ModelContractVersion",
    "PageModelSectionSpec",
    "ApplicantApplicationHomePageModel",
    "ApplicantApplicationEditorPageModel",
    "ReviewApplicationPageModel",
    "AdminDashboardPageModel",
    "PageModelSectionCatalog",
]
