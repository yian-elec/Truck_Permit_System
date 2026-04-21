"""
UC-OPS-04 — 外部資料匯入 DTO。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleImportJobInputDTO(BaseModel):
    """建立匯入作業（map／holiday／routing rules 等以 job_type 區分）。"""

    job_type: str = Field(..., min_length=1, max_length=50)
    source_name: str = Field(..., min_length=1, max_length=100)
    source_ref: Optional[str] = Field(None, max_length=255)


class ScheduleImportJobOutputDTO(BaseModel):
    import_job_id: UUID
    status: str


class RunImportPipelineInputDTO(BaseModel):
    """執行匯入：抓外部資料 → 標準化 → 寫業務表等由 ImportSinkPort 封裝。"""

    import_job_id: UUID


class RunImportPipelineOutputDTO(BaseModel):
    import_job_id: UUID
    status: str
    result_summary: Optional[str] = None


class ImportJobListItemDTO(BaseModel):
    import_job_id: UUID
    job_type: str
    source_name: str
    source_ref: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ImportJobDetailDTO(BaseModel):
    """匯入作業詳情（與列表欄位相同，預留擴充）。"""

    job: ImportJobListItemDTO
