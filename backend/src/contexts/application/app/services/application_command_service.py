"""
申請案件用例外觀（Facade）。

責任：對 API／上層模組提供單一進入點 `ApplicationCommandService`，內部委派至依 UC 劃分之專責服務，
維持方法簽名穩定；實際流程與依賴注入見 `ApplicationServiceContext` 與各 `*ApplicationService`。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.application.domain.repositories import ApplicationReadModelQuery
from src.contexts.application.infra.repositories import (
    ApplicationReadModelQueryImpl,
    ApplicationRepositoryImpl,
)

from ..dtos import (
    AddVehicleInputDTO,
    ApplicationDetailDTO,
    ApplicationEditModelDTO,
    ApplicationSummaryDTO,
    AttachmentSummaryDTO,
    CompleteAttachmentUploadInputDTO,
    CreateDraftApplicationInputDTO,
    CreateDraftApplicationOutputDTO,
    DownloadUrlOutputDTO,
    PatchApplicationInputDTO,
    PatchApplicationProfilesInputDTO,
    PatchVehicleInputDTO,
    PresignedUploadUrlOutputDTO,
    RequestUploadUrlInputDTO,
    StatusHistoryEntryDTO,
    SubmissionCheckResultDTO,
    SubmitApplicationOutputDTO,
    SupplementRequestItemDTO,
    SupplementResponseInputDTO,
    SupplementResponseOutputDTO,
    VehicleDTO,
)
from ._policy import DEFAULT_MAX_PERMIT_CALENDAR_DAYS
from .application_query_service import ApplicationQueryService
from .application_service_context import ApplicationServiceContext
from .attachment_application_service import AttachmentApplicationService
from .draft_application_service import DraftApplicationService
from .ports.outbound import (
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


class ApplicationCommandService:
    """
    申請人端申請案件之命令／查詢用例外觀。

    責任：組合專責服務並轉發呼叫；本身不含業務分支邏輯。
    """

    def __init__(
        self,
        *,
        repository: ApplicationRepositoryImpl | None = None,
        read_model: ApplicationReadModelQuery | None = None,
        file_storage: FileStoragePort | None = None,
        event_publisher: ApplicationEventPublisher | None = None,
        supplement_workflow: SupplementWorkflowPort | None = None,
        max_permit_calendar_days: int = DEFAULT_MAX_PERMIT_CALENDAR_DAYS,
    ) -> None:
        repo = repository or ApplicationRepositoryImpl()
        read = read_model or ApplicationReadModelQueryImpl()
        files = file_storage or NoopFileStoragePort()
        events = event_publisher or NoopApplicationEventPublisher()
        supplement = supplement_workflow or NoopSupplementWorkflowPort()
        ctx = ApplicationServiceContext(
            repository=repo,
            read_model=read,
            file_storage=files,
            event_publisher=events,
            supplement_workflow=supplement,
            max_permit_calendar_days=max_permit_calendar_days,
        )
        self._draft = DraftApplicationService(ctx)
        self._vehicles = VehicleApplicationService(ctx)
        self._attachments = AttachmentApplicationService(ctx)
        self._submission = SubmissionApplicationService(ctx)
        self._supplement = SupplementApplicationService(ctx)
        self._queries = ApplicationQueryService(ctx)

    # --- UC-APP-01 / 02 / consent ---
    def create_draft(
        self,
        dto: CreateDraftApplicationInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> CreateDraftApplicationOutputDTO:
        return self._draft.create_draft(dto, applicant_user_id=applicant_user_id)

    def update_draft_application(
        self,
        application_id: UUID,
        *,
        patch: PatchApplicationInputDTO | None = None,
        profiles: PatchApplicationProfilesInputDTO | None = None,
        applicant_user_id: UUID | None,
    ) -> ApplicationDetailDTO:
        return self._draft.update_draft_application(
            application_id,
            patch=patch,
            profiles=profiles,
            applicant_user_id=applicant_user_id,
        )

    def record_consent(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> ApplicationDetailDTO:
        return self._draft.record_consent(application_id, applicant_user_id=applicant_user_id)

    # --- UC-APP-03 ---
    def add_vehicle(
        self,
        application_id: UUID,
        dto: AddVehicleInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> list[VehicleDTO]:
        return self._vehicles.add_vehicle(application_id, dto, applicant_user_id=applicant_user_id)

    def update_vehicle(
        self,
        application_id: UUID,
        vehicle_id: UUID,
        dto: PatchVehicleInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> list[VehicleDTO]:
        return self._vehicles.update_vehicle(
            application_id,
            vehicle_id,
            dto,
            applicant_user_id=applicant_user_id,
        )

    def remove_vehicle(
        self,
        application_id: UUID,
        vehicle_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[VehicleDTO]:
        return self._vehicles.remove_vehicle(
            application_id,
            vehicle_id,
            applicant_user_id=applicant_user_id,
        )

    # --- UC-APP-04 ---
    def create_attachment_upload_url(
        self,
        application_id: UUID,
        dto: RequestUploadUrlInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> PresignedUploadUrlOutputDTO:
        return self._attachments.create_attachment_upload_url(
            application_id,
            dto,
            applicant_user_id=applicant_user_id,
        )

    def complete_attachment_upload(
        self,
        application_id: UUID,
        dto: CompleteAttachmentUploadInputDTO,
        *,
        applicant_user_id: UUID | None,
        uploaded_by: UUID | None = None,
    ) -> AttachmentSummaryDTO:
        return self._attachments.complete_attachment_upload(
            application_id,
            dto,
            applicant_user_id=applicant_user_id,
            uploaded_by=uploaded_by,
        )

    def list_attachments(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[AttachmentSummaryDTO]:
        return self._attachments.list_attachments(application_id, applicant_user_id=applicant_user_id)

    def get_attachment_download_url(
        self,
        application_id: UUID,
        attachment_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> DownloadUrlOutputDTO:
        return self._attachments.get_attachment_download_url(
            application_id,
            attachment_id,
            applicant_user_id=applicant_user_id,
        )

    def delete_attachment(
        self,
        application_id: UUID,
        attachment_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> None:
        self._attachments.delete_attachment(
            application_id,
            attachment_id,
            applicant_user_id=applicant_user_id,
        )

    # --- UC-APP-05 / 06 ---
    def submission_check(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> SubmissionCheckResultDTO:
        return self._submission.submission_check(application_id, applicant_user_id=applicant_user_id)

    def submit_application(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
        changed_by: UUID | None = None,
    ) -> SubmitApplicationOutputDTO:
        return self._submission.submit_application(
            application_id,
            applicant_user_id=applicant_user_id,
            changed_by=changed_by,
        )

    # --- UC-APP-07 ---
    def list_supplement_requests(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[SupplementRequestItemDTO]:
        return self._supplement.list_supplement_requests(
            application_id,
            applicant_user_id=applicant_user_id,
        )

    def supplement_response(
        self,
        application_id: UUID,
        dto: SupplementResponseInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> SupplementResponseOutputDTO:
        return self._supplement.supplement_response(
            application_id,
            dto,
            applicant_user_id=applicant_user_id,
        )

    # --- 查詢 ---
    def get_application(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> ApplicationDetailDTO:
        return self._queries.get_application(application_id, applicant_user_id=applicant_user_id)

    def list_applications_for_applicant(
        self,
        applicant_user_id: UUID,
        *,
        limit: int = 100,
    ) -> list[ApplicationSummaryDTO]:
        return self._queries.list_applications_for_applicant(applicant_user_id, limit=limit)

    def get_edit_model(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> ApplicationEditModelDTO:
        return self._queries.get_edit_model(application_id, applicant_user_id=applicant_user_id)

    def get_timeline(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[StatusHistoryEntryDTO]:
        return self._queries.get_timeline(application_id, applicant_user_id=applicant_user_id)
