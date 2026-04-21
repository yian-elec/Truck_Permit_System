"""
Application context — Domain 層（DDD）。

結構對照規格 5.1：
- **Aggregate Root**：`Application`（一致性邊界，協調子實體與 AttachmentBundle）。
- **實體**：`ApplicantProfile`、`CompanyProfile`、`Vehicle`、`ChecklistItem`、`StatusHistoryEntry` 等
  （具身分識別、生命週期隸屬於本聚合）。
- **值物件**：`ApplicationStatus`、`PermitPeriod`、`VehiclePlate`、`AttachmentType`、`DeliveryMethod` 等
  （不可變、以值相等、內含校驗）。
- **領域錯誤**：`application.domain.errors`（表達不變條件與狀態機違例）。
- **儲存庫／查詢埠**：`ApplicationRepository`、`ApplicationReadModelQuery`（介面在此，實作在 Infra）。

依賴說明：僅使用標準函式庫與 `shared.errors.domain_error.DomainError` 作為例外基底（跨 context 之型別共用），
**不**依賴 App、API、SQLAlchemy 或任何 Infra 實作。
"""

from .entities import (
    MAX_VEHICLES_PER_APPLICATION,
    ApplicantProfile,
    Application,
    AttachmentBundle,
    AttachmentDescriptor,
    ChecklistItem,
    CompanyProfile,
    StatusHistoryEntry,
    SubmissionReadiness,
    Vehicle,
)
from .errors import (
    ApplicationDomainError,
    ConsentRequiredError,
    CoreDataNotEditableError,
    InvalidApplicationStateError,
    InvalidDomainValueError,
    RouteRequestMissingError,
    SubmissionRequirementsNotMetError,
    VehicleLimitExceededError,
)
from .repositories import ApplicationReadModelQuery, ApplicationRepository
from .value_objects import (
    ApplicantType,
    ApplicationStatus,
    ApplicationStatusPhase,
    AttachmentType,
    DeliveryMethod,
    PermitPeriod,
    ReasonType,
    SourceChannel,
    VehiclePlate,
)

__all__ = [
    "MAX_VEHICLES_PER_APPLICATION",
    "Application",
    "ApplicantProfile",
    "CompanyProfile",
    "Vehicle",
    "AttachmentBundle",
    "AttachmentDescriptor",
    "ChecklistItem",
    "StatusHistoryEntry",
    "SubmissionReadiness",
    "ApplicationStatus",
    "ApplicationStatusPhase",
    "PermitPeriod",
    "VehiclePlate",
    "AttachmentType",
    "DeliveryMethod",
    "ApplicantType",
    "ReasonType",
    "SourceChannel",
    "ApplicationDomainError",
    "InvalidDomainValueError",
    "InvalidApplicationStateError",
    "CoreDataNotEditableError",
    "SubmissionRequirementsNotMetError",
    "VehicleLimitExceededError",
    "ConsentRequiredError",
    "RouteRequestMissingError",
    "ApplicationRepository",
    "ApplicationReadModelQuery",
]
