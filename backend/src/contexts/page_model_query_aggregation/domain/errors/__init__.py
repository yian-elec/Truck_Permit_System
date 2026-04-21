"""
Page_Model_Query_Aggregation — 領域錯誤匯出。
"""

from .page_model_errors import (
    DuplicateSectionOrderError,
    InvalidPageModelCompositionError,
    PageModelDomainError,
    PrerequisiteSectionMissingError,
    UnknownSectionCodeError,
)

__all__ = [
    "PageModelDomainError",
    "InvalidPageModelCompositionError",
    "UnknownSectionCodeError",
    "DuplicateSectionOrderError",
    "PrerequisiteSectionMissingError",
]
