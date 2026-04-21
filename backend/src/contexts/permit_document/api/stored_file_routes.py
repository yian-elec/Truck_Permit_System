"""
許可證 PDF 之本機簽名下載（GET，無 JWT；以 HMAC + 短期 expires 保護）。

責任：與 **LocalSignedDownloadStoragePort** 回傳之 URL 對齊；回傳原始 **FileResponse**（非信封 JSON）。
"""

from __future__ import annotations

from time import time
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from src.contexts.permit_document.app.services import (
    PermitServiceContext,
    build_default_permit_service_context_dependencies,
)
from src.contexts.permit_document.app.services.certificate_generation_application_service import (
    CertificateGenerationApplicationService,
)
from src.contexts.permit_document.infra.permit_local_storage import (
    permit_certificate_pdf_path,
    verify_download,
)

router = APIRouter(prefix="/api/v1", tags=["檔案下載（簽章）"])


def _try_materialize_permit_pdf_if_missing(file_id: UUID) -> bool:
    """磁碟缺檔時依 DB 之 active 文件列補寫 PDF。"""
    auth, storage = build_default_permit_service_context_dependencies()
    ctx = PermitServiceContext(authorization=auth, object_storage=storage)
    return CertificateGenerationApplicationService(ctx).ensure_local_permit_pdf_file(file_id)


@router.get(
    "/stored-files/{file_id}/download",
    summary="依簽章下載已儲存檔案（許可證 PDF）",
    description=(
        "由 **POST …/permit/download-url** 回傳之短期連結；使用 **expires**（Unix 秒）與 **sig**（HMAC-SHA256 hex）。"
        "若本機目錄缺檔但 DB 仍有 **active** 之文件列，將於此請求內依許可重畫 PDF 後回傳。"
    ),
    responses={
        200: {"description": "PDF 位元組"},
        403: {"description": "簽章無效"},
        404: {"description": "檔案不存在"},
        410: {"description": "連結已過期"},
    },
)
async def get_stored_file_download(
    file_id: UUID,
    expires: int = Query(..., description="過期時間（Unix 時間戳，秒）"),
    sig: str = Query(..., description="HMAC-SHA256（hex）"),
) -> FileResponse:
    if time() > expires:
        raise HTTPException(status_code=410, detail="Download link expired")
    if not verify_download(file_id, expires, sig):
        raise HTTPException(status_code=403, detail="Invalid signature")
    path = permit_certificate_pdf_path(file_id)
    if not path.is_file() and not _try_materialize_permit_pdf_if_missing(file_id):
        raise HTTPException(
            status_code=404,
            detail="File not found on server (regenerate certificate or check storage path)",
        )
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"permit_{file_id}.pdf",
    )
