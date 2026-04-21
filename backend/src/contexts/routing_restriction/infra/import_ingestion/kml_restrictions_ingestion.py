"""
UC-ROUTE-06：實作 Integration_Operations 之 ImportIngestionPort，將 kml_restrictions job 轉交 KML 管線。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.integration_operations.app.services.ports.external_ports import (
    ImportIngestionPort,
)
from src.contexts.routing_restriction.infra.kml.import_context import get_pending_kml_body
from src.contexts.routing_restriction.infra.kml.pipeline import run_kml_import

KML_RESTRICTIONS_JOB_TYPE = "kml_restrictions"
# 完整內容超過 ops.import_jobs.source_ref(255) 時寫入佔位字串，實際 URL／KML 經 ContextVar 傳入 ingest。
INLINE_KML_PLACEHOLDER_REF = "inline_kml"
LONG_URL_PLACEHOLDER_REF = "http_url_long"


class KmlRestrictionsImportIngestion(ImportIngestionPort):
    """僅處理 job_type=kml_restrictions；其餘型別拋錯使 job 標記失敗。"""

    def ingest(
        self,
        *,
        import_job_id: UUID,
        job_type: str,
        source_name: str,
        source_ref: str | None,
    ) -> str:
        _ = import_job_id
        if job_type != KML_RESTRICTIONS_JOB_TYPE:
            raise ValueError(f"unsupported import job_type: {job_type}")
        pending = get_pending_kml_body()
        if pending is not None and str(pending).strip():
            return run_kml_import(pending.strip())
        if not source_ref or not str(source_ref).strip():
            raise ValueError("source_ref is required for kml_restrictions import")
        ref = source_ref.strip()
        if ref in (INLINE_KML_PLACEHOLDER_REF, LONG_URL_PLACEHOLDER_REF):
            raise ValueError("full KML source was not provided (context missing)")
        return run_kml_import(ref)
