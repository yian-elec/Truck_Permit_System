"""
附件上傳與查詢 DTO。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequestUploadUrlInputDTO(BaseModel):
    """申請上傳 URL 時之輸入（由 API 層填入 file_id 或於服務內產生）。"""

    file_id: UUID | None = Field(None, description="未傳則由服務端產生新 UUID")
    mime_type: str = Field(..., max_length=100)


class PresignedUploadUrlOutputDTO(BaseModel):
    """UC-APP-04 取得上傳 URL 之回應（實際 URL 由 FileStoragePort 產生）。"""

    upload_url: str = Field(..., description="前端直傳物件儲存之上傳網址")
    object_key: str = Field(..., description="物件鍵，完成上傳時須回傳")
    file_id: UUID = Field(..., description="預先配置的檔案識別，與 complete 一致")


class CompleteAttachmentUploadInputDTO(BaseModel):
    """UC-APP-04 上傳完成回報：寫入 stored_files 與 attachments。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    file_id: UUID
    attachment_id: UUID
    attachment_type: str = Field(..., max_length=50)
    original_filename: str = Field(..., max_length=255)
    mime_type: str = Field(..., max_length=100)
    size_bytes: int = Field(..., ge=0)
    checksum_sha256: str = Field(..., min_length=64, max_length=64)
    bucket_name: str = Field(..., max_length=100)
    object_key: str = Field(..., max_length=255)
    storage_provider: str = Field(..., max_length=30)
    virus_scan_status: str = Field(default="clean", max_length=30)
    status: str = Field(default="uploaded", max_length=30)
    ocr_status: str = Field(default="pending", max_length=30)
    uploaded_at: datetime | None = Field(
        None,
        description="未傳則由服務端以當下 UTC 時間填入",
    )


class AttachmentSummaryDTO(BaseModel):
    """附件列表／明細摘要。"""

    attachment_id: UUID
    attachment_type: str
    file_id: UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    status: str
    ocr_status: str
    uploaded_by: UUID | None
    uploaded_at: datetime


class DownloadUrlOutputDTO(BaseModel):
    """附件下載 presigned URL。"""

    download_url: str
    expires_at: datetime | None = None
