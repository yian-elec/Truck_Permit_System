"""
UC-OPS-01 — OCR 附件相關 DTO。

責任：描述 AttachmentUploaded 後排程 OCR、以及管線執行時的輸入／輸出邊界（API / 訊息匯流排使用）。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleOcrJobInputDTO(BaseModel):
    """建立 OCR 作業（對應「接收 AttachmentUploaded → 建立 ocr job」）。"""

    attachment_id: UUID = Field(..., description="附件識別（他界 context）")
    provider_code: str = Field(..., min_length=1, max_length=50, description="OCR 供應商代碼")


class ScheduleOcrJobOutputDTO(BaseModel):
    """排程成功後回傳作業識別與初始狀態。"""

    ocr_job_id: UUID
    status: str
    attachment_id: UUID


class RunOcrPipelineInputDTO(BaseModel):
    """觸發既有 OCR 作業之執行管線（取檔 → provider → 寫結果）。"""

    ocr_job_id: UUID = Field(..., description="待執行之 ocr_job_id")


class OcrExtractedFieldDTO(BaseModel):
    """單一欄位辨識結果（由 OcrExtractorPort 回傳，供 App 轉成 Domain OcrResult）。"""

    field_name: str = Field(..., min_length=1, max_length=100)
    field_value: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    raw_json: Optional[dict[str, Any]] = None


class RunOcrPipelineOutputDTO(BaseModel):
    """管線完成摘要。"""

    ocr_job_id: UUID
    status: str
    result_count: int = Field(..., ge=0, description="寫入之 ocr_results 筆數")


class OcrJobListItemDTO(BaseModel):
    """列表 API 用 OCR 作業摘要。"""

    ocr_job_id: UUID
    attachment_id: UUID
    provider_code: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class OcrResultItemDTO(BaseModel):
    """單筆 OCR 結果（詳情 API 用）。"""

    ocr_result_id: UUID
    attachment_id: UUID
    field_name: str
    field_value: Optional[str] = None
    confidence: Optional[float] = None
    raw_json: Optional[dict[str, Any]] = None
    created_at: datetime


class OcrJobDetailDTO(BaseModel):
    """OCR 作業詳情（含結果列表）。"""

    job: OcrJobListItemDTO
    results: list[OcrResultItemDTO] = Field(default_factory=list)
