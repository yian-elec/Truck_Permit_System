"""Permit_Document — DTO 匯出。"""

from .permit_command_dtos import (
    CreatePermitInputDTO,
    CreatePermitOutputDTO,
    RecordDocumentJobCompletedInputDTO,
    RegisterGeneratedDocumentInputDTO,
    RequestDocumentRegenerationInputDTO,
    RequestDocumentRegenerationOutputDTO,
)
from .permit_query_dtos import (
    ApplicantPermitDocumentDownloadBodyDTO,
    CreateDocumentDownloadUrlInputDTO,
    CreateDocumentDownloadUrlOutputDTO,
    GetPermitByApplicationQueryDTO,
    GetPermitByIdQueryDTO,
    ListPermitDocumentsOutputDTO,
    ListPermitDocumentsQueryDTO,
    PermitDocumentRowDTO,
    PermitSummaryDTO,
    RequestPermitDocumentDownloadByApplicationDTO,
)

__all__ = [
    "CreatePermitInputDTO",
    "CreatePermitOutputDTO",
    "RequestDocumentRegenerationInputDTO",
    "RequestDocumentRegenerationOutputDTO",
    "RecordDocumentJobCompletedInputDTO",
    "RegisterGeneratedDocumentInputDTO",
    "PermitSummaryDTO",
    "PermitDocumentRowDTO",
    "GetPermitByApplicationQueryDTO",
    "GetPermitByIdQueryDTO",
    "ListPermitDocumentsQueryDTO",
    "ListPermitDocumentsOutputDTO",
    "CreateDocumentDownloadUrlInputDTO",
    "CreateDocumentDownloadUrlOutputDTO",
    "ApplicantPermitDocumentDownloadBodyDTO",
    "RequestPermitDocumentDownloadByApplicationDTO",
]
