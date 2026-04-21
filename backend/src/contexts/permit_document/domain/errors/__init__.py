"""
Permit_Document — 領域錯誤匯出。

責任：供 domain 套件內模組與後續 App 層辨識業務違例；各類別用途見 permit_errors.py。
"""

from .permit_errors import (
    DocumentJobStateError,
    InvalidPermitStateError,
    InvalidPermitValueError,
    PermitCreationPreconditionError,
    PermitDocumentStateError,
    PermitDomainError,
)

__all__ = [
    "PermitDomainError",
    "InvalidPermitValueError",
    "InvalidPermitStateError",
    "PermitCreationPreconditionError",
    "PermitDocumentStateError",
    "DocumentJobStateError",
]
