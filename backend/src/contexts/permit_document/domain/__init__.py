"""
Permit_Document bounded context — Domain 套件。

責任：匯出聚合根、實體、值物件與領域錯誤；不含 Infra／App／API。
"""

from src.contexts.permit_document.domain.entities import (
    PENDING_FILE_ID_PLACEHOLDER,
    DocumentGenerationJob,
    Permit,
    PermitDocument,
)
from src.contexts.permit_document.domain.errors import (
    DocumentJobStateError,
    InvalidPermitStateError,
    InvalidPermitValueError,
    PermitCreationPreconditionError,
    PermitDocumentStateError,
    PermitDomainError,
)
from src.contexts.permit_document.domain.value_objects import (
    DocumentBundle,
    DocumentJobStatus,
    DocumentJobStatusPhase,
    DocumentJobType,
    DocumentJobTypePhase,
    DocumentRef,
    DocumentTypeCode,
    DocumentTypeCodePhase,
    FinalRouteBinding,
    PermitAggregateStatus,
    PermitAggregateStatusPhase,
    PermitStatus,
    PermitStatusPhase,
    PermitApprovedPeriod,
    PermitDocumentRecordStatus,
    PermitDocumentRecordStatusPhase,
    PermitNo,
    RouteSummaryText,
)

__all__ = [
    "Permit",
    "PermitDocument",
    "DocumentGenerationJob",
    "PENDING_FILE_ID_PLACEHOLDER",
    "PermitDomainError",
    "InvalidPermitValueError",
    "InvalidPermitStateError",
    "PermitCreationPreconditionError",
    "PermitDocumentStateError",
    "DocumentJobStateError",
    "PermitNo",
    "PermitStatus",
    "PermitStatusPhase",
    "PermitAggregateStatus",
    "PermitAggregateStatusPhase",
    "PermitDocumentRecordStatus",
    "PermitDocumentRecordStatusPhase",
    "RouteSummaryText",
    "DocumentRef",
    "PermitApprovedPeriod",
    "FinalRouteBinding",
    "DocumentTypeCode",
    "DocumentTypeCodePhase",
    "DocumentJobType",
    "DocumentJobStatus",
    "DocumentJobTypePhase",
    "DocumentJobStatusPhase",
    "DocumentBundle",
]
