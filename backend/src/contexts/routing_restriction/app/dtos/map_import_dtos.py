"""
UC-ROUTE-06：KML 匯入作業相關 DTO（佔位，待與實際 job 儲存對接）。

責任：描述 API 契約；實際寫入 import job 由後續迭代完成。
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class RequestKmlImportInputDTO(BaseModel):
    """請求建立 KML 匯入作業（可為檔案識別或 URL）。"""

    source_description: str = Field(..., min_length=1, description="檔案鍵、URL 或內部參考")


class MapImportJobStatusDTO(BaseModel):
    """匯入作業狀態。"""

    import_job_id: UUID
    status: str
    message: str | None = None
