"""Permit_Document — 應用層錯誤匯出。"""

from .permit_app_errors import (
    PermitAppError,
    PermitCertificateFontError,
    PermitConflictAppError,
    PermitForbiddenAppError,
    PermitNotFoundAppError,
    PermitValidationAppError,
    map_permit_domain_exception_to_app,
    raise_permit_domain_as_app,
)

__all__ = [
    "PermitAppError",
    "PermitCertificateFontError",
    "PermitNotFoundAppError",
    "PermitValidationAppError",
    "PermitConflictAppError",
    "PermitForbiddenAppError",
    "map_permit_domain_exception_to_app",
    "raise_permit_domain_as_app",
]
