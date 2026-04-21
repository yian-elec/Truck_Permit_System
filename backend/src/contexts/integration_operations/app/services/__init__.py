"""
Integration_Operations — Application 服務（用例編排）。

依賴注入建議（API 層組裝）：
- OcrAttachmentApplicationService(repository, AttachmentBlobPort, OcrExtractorPort, AttachmentOcrStatusPort?)
- NotificationApplicationService(repository, NotificationDispatchPort)
- AuditApplicationService(repository)
- ImportApplicationService(repository, ImportIngestionPort)
- OpsQueryApplicationService(OpsReadPort) — 可傳入 OpsReadRepositoryImpl
"""

from .audit_application_service import AuditApplicationService
from .import_application_service import ImportApplicationService
from .notification_application_service import NotificationApplicationService
from .ocr_attachment_application_service import OcrAttachmentApplicationService
from .ops_query_application_service import OpsQueryApplicationService
from .ports import (
    AttachmentBlobPort,
    AttachmentOcrStatusPort,
    ImportIngestionPort,
    NotificationDispatchPort,
    OcrExtractorPort,
    OpsReadPort,
)

__all__ = [
    "OpsReadPort",
    "AttachmentBlobPort",
    "OcrExtractorPort",
    "AttachmentOcrStatusPort",
    "NotificationDispatchPort",
    "ImportIngestionPort",
    "OcrAttachmentApplicationService",
    "NotificationApplicationService",
    "AuditApplicationService",
    "ImportApplicationService",
    "OpsQueryApplicationService",
]
