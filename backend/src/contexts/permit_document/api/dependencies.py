"""
Permit_Document API — 依賴注入。

責任：組合 **PermitServiceContext** 與命令／查詢應用服務；JWT 之操作者識別沿用
**Application** context 之 `get_applicant_user_id`（與申請人端 API 一致）。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.application.api.dependencies import get_applicant_user_id
from src.contexts.permit_document.app.services import (
    PermitCommandApplicationService,
    PermitQueryApplicationService,
    PermitServiceContext,
    build_default_permit_service_context_dependencies,
)


@dataclass
class PermitApiBundle:
    """HTTP 層一次注入之許可證用例服務組。"""

    p_cmd: PermitCommandApplicationService
    p_qry: PermitQueryApplicationService


def get_permit_api_bundle() -> PermitApiBundle:
    """
    建立預設 **PermitApiBundle**（開發用 Authorization／Storage 埠實作）。

    責任：與本地／整合測試相同之組合；正式環境應改為依設定注入真實 Port。
    """
    auth, storage = build_default_permit_service_context_dependencies()
    ctx = PermitServiceContext(authorization=auth, object_storage=storage)
    return PermitApiBundle(
        p_cmd=PermitCommandApplicationService(ctx),
        p_qry=PermitQueryApplicationService(ctx),
    )


# 別名：語意上為「目前 JWT 對應之操作者」，與申請人端許可 API 共用。
get_permit_actor_user_id = get_applicant_user_id
