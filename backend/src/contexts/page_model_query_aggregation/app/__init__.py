"""
Page_Model_Query_Aggregation — Application 層。

責任：用例服務、DTO、應用層錯誤；協調 Domain 與可選 Infra（快照 repository）。
"""

from .dtos import (
    AdminDashboardPageInputDTO,
    ApplicantApplicationEditorInputDTO,
    ApplicantApplicationHomeInputDTO,
    PageModelQueryResultDTO,
    PageSectionItemDTO,
    ReviewApplicationPageInputDTO,
)
from .errors import (
    PageModelAppError,
    PageModelConflictAppError,
    PageModelInternalAppError,
    PageModelValidationAppError,
    map_page_model_domain_exception_to_app,
    raise_page_model_domain_as_app,
)
from .services import (
    PageModelQueryApplicationService,
    PageModelServiceContext,
)

__all__ = [
    "PageSectionItemDTO",
    "PageModelQueryResultDTO",
    "ApplicantApplicationHomeInputDTO",
    "ApplicantApplicationEditorInputDTO",
    "ReviewApplicationPageInputDTO",
    "AdminDashboardPageInputDTO",
    "PageModelAppError",
    "PageModelValidationAppError",
    "PageModelConflictAppError",
    "PageModelInternalAppError",
    "map_page_model_domain_exception_to_app",
    "raise_page_model_domain_as_app",
    "PageModelServiceContext",
    "PageModelQueryApplicationService",
]
