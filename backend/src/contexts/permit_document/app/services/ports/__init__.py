"""Permit_Document — 應用層出站埠（Protocol）與開發用預設實作。"""

from .default_adapters import (
    LocalSignedDownloadStoragePort,
    PermissivePermitAuthorizationPort,
    PlaceholderObjectStoragePort,
    build_default_permit_service_context_dependencies,
)
from .outbound import PermitAuthorizationPort, PermitObjectStoragePort

__all__ = [
    "PermitAuthorizationPort",
    "PermitObjectStoragePort",
    "PermissivePermitAuthorizationPort",
    "PlaceholderObjectStoragePort",
    "LocalSignedDownloadStoragePort",
    "build_default_permit_service_context_dependencies",
]
