"""
Application App 層 — 用例服務。

目錄約定：
- **專責服務**：依 UC 邊界拆分（draft／vehicle／attachment／submission／supplement／query）
- **外觀**：`ApplicationCommandService` 供上層單一注入
- **上下文**：`ApplicationServiceContext` 共用依賴與載入／儲存輔助
- **埠**：`ports/` 子套件（Outbound protocols），避免在 `app` 根目錄與 dtos／errors 並列
"""

from .application_command_service import ApplicationCommandService
from .application_query_service import ApplicationQueryService
from .application_service_context import ApplicationServiceContext
from .attachment_application_service import AttachmentApplicationService
from .draft_application_service import DraftApplicationService
from .public_heavy_truck_service import PublicHeavyTruckPermitService
from .ports import (
    ApplicationEventPublisher,
    FileStoragePort,
    NoopApplicationEventPublisher,
    NoopFileStoragePort,
    NoopSupplementWorkflowPort,
    SupplementWorkflowPort,
)
from .submission_application_service import SubmissionApplicationService
from .supplement_application_service import SupplementApplicationService
from .vehicle_application_service import VehicleApplicationService

__all__ = [
    "ApplicationCommandService",
    "ApplicationServiceContext",
    "DraftApplicationService",
    "PublicHeavyTruckPermitService",
    "VehicleApplicationService",
    "AttachmentApplicationService",
    "SubmissionApplicationService",
    "SupplementApplicationService",
    "ApplicationQueryService",
    "FileStoragePort",
    "ApplicationEventPublisher",
    "SupplementWorkflowPort",
    "NoopFileStoragePort",
    "NoopApplicationEventPublisher",
    "NoopSupplementWorkflowPort",
]
