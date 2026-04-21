"""
附件用例（UC-APP-04）。

責任：上傳 URL、完成寫庫、列表、下載 URL、刪除；依賴 FileStoragePort 與 Repository 附件 API。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from ..dtos import (
    AttachmentSummaryDTO,
    CompleteAttachmentUploadInputDTO,
    DownloadUrlOutputDTO,
    PresignedUploadUrlOutputDTO,
    RequestUploadUrlInputDTO,
)
from ..errors import ApplicationNotFoundAppError, to_app_error
from .application_mappers import attachment_view_to_dto
from .application_service_context import ApplicationServiceContext


class AttachmentApplicationService:
    """UC-APP-04 專責服務。"""

    def __init__(self, ctx: ApplicationServiceContext) -> None:
        self._c = ctx

    def create_attachment_upload_url(
        self,
        application_id: UUID,
        dto: RequestUploadUrlInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> PresignedUploadUrlOutputDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        file_id = dto.file_id or uuid4()
        object_key = f"applications/{application_id}/{file_id}"
        url = self._c.files.create_presigned_upload_url(
            application_id=application_id,
            file_id=file_id,
            object_key=object_key,
            mime_type=dto.mime_type,
        )
        return PresignedUploadUrlOutputDTO(
            upload_url=url,
            object_key=object_key,
            file_id=file_id,
        )

    def complete_attachment_upload(
        self,
        application_id: UUID,
        dto: CompleteAttachmentUploadInputDTO,
        *,
        applicant_user_id: UUID | None,
        uploaded_by: UUID | None = None,
    ) -> AttachmentSummaryDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        uploaded_at = dto.uploaded_at or datetime.now(timezone.utc)
        uid = uploaded_by if uploaded_by is not None else applicant_user_id
        try:
            self._c.repo.persist_attachment_upload(
                application_id=application_id,
                attachment_id=dto.attachment_id,
                file_id=dto.file_id,
                attachment_type=dto.attachment_type,
                original_filename=dto.original_filename,
                mime_type=dto.mime_type,
                size_bytes=dto.size_bytes,
                checksum_sha256=dto.checksum_sha256,
                status=dto.status,
                ocr_status=dto.ocr_status,
                uploaded_by=uid,
                uploaded_at=uploaded_at,
                bucket_name=dto.bucket_name,
                object_key=dto.object_key,
                storage_provider=dto.storage_provider,
                virus_scan_status=dto.virus_scan_status,
            )
        except Exception as e:
            raise to_app_error(e) from e
        self._c.events.publish(
            "AttachmentUploaded",
            {
                "application_id": str(application_id),
                "attachment_id": str(dto.attachment_id),
                "file_id": str(dto.file_id),
                "attachment_type": dto.attachment_type,
            },
        )
        views = self._c.read.list_attachment_summaries(application_id)
        match = next((v for v in views if v.attachment_id == dto.attachment_id), None)
        if match is None:
            raise ApplicationNotFoundAppError("附件寫入後讀取失敗")
        return attachment_view_to_dto(match)

    def list_attachments(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[AttachmentSummaryDTO]:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        return [
            attachment_view_to_dto(v)
            for v in self._c.read.list_attachment_summaries(application_id)
        ]

    def get_attachment_download_url(
        self,
        application_id: UUID,
        attachment_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> DownloadUrlOutputDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        views = self._c.read.list_attachment_summaries(application_id)
        match = next((v for v in views if v.attachment_id == attachment_id), None)
        if match is None:
            raise ApplicationNotFoundAppError(
                "附件不存在",
                details={"attachment_id": str(attachment_id)},
            )
        url = self._c.files.create_presigned_download_url(object_key=f"stub/{attachment_id}")
        return DownloadUrlOutputDTO(download_url=url, expires_at=None)

    def delete_attachment(
        self,
        application_id: UUID,
        attachment_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> None:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        try:
            self._c.repo.delete_attachment_and_reconcile(
                application_id=application_id,
                attachment_id=attachment_id,
            )
        except Exception as e:
            raise to_app_error(e) from e
