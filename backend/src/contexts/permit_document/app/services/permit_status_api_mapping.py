"""
Permit／Certificate 狀態：持久化字串 ↔ §8 API 顯示名稱。

責任：集中映射，避免路由層散落字串；DB 可保留歷史別名（如舊種子資料）。
"""

from __future__ import annotations

# permit.permits.status（內部）→ 對外 §8
PERMIT_STATUS_TO_API: dict[str, str] = {
    "pending_generation": "pending_generation",
    "pending_documents": "pending_generation",
    "issued": "issued",
    "generation_failed": "generation_failed",
    "issued_pending_document_regen": "issued",
    "revoked": "revoked",
    "expired": "expired",
}

# permit.documents.status → 對外 certificate.status（§8）
CERTIFICATE_STATUS_TO_API: dict[str, str] = {
    "pending": "queued",
    "queued": "queued",
    "processing": "processing",
    "active": "generated",
    "generated": "generated",
    "failed": "failed",
    "superseded": "superseded",
}


def permit_status_to_api(internal: str) -> str:
    return PERMIT_STATUS_TO_API.get(internal, internal)


def certificate_status_to_api(internal: str) -> str:
    return CERTIFICATE_STATUS_TO_API.get(internal, internal)
