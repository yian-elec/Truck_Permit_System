"""
Permit 用例服務共用執行上下文。

責任：集中注入 **Repositories**、**IssuanceContextReader**、出站 **Port**；
各 `*ApplicationService` 僅依賴本上下文，避免建構子參數膨脹。
"""

from __future__ import annotations

from src.contexts.permit_document.app.services.integrations import PermitIssuanceContextReader
from src.contexts.permit_document.app.services.permit_issuance_load_port import PermitIssuanceLoadPort
from src.contexts.permit_document.app.services.ports.outbound import (
    PermitAuthorizationPort,
    PermitObjectStoragePort,
)
from src.contexts.permit_document.infra.repositories import (
    CertificateAccessLogsRepository,
    DocumentJobsRepository,
    DocumentsRepository,
    PermitsRepository,
)


class PermitServiceContext:
    """Permit_Document 應用服務依賴封裝。"""

    def __init__(
        self,
        *,
        permits: PermitsRepository | None = None,
        documents: DocumentsRepository | None = None,
        jobs: DocumentJobsRepository | None = None,
        certificate_access_logs: CertificateAccessLogsRepository | None = None,
        issuance_reader: PermitIssuanceLoadPort | None = None,
        authorization: PermitAuthorizationPort,
        object_storage: PermitObjectStoragePort,
    ) -> None:
        self.permits = permits or PermitsRepository()
        self.documents = documents or DocumentsRepository()
        self.jobs = jobs or DocumentJobsRepository()
        self.certificate_access_logs = certificate_access_logs or CertificateAccessLogsRepository()
        self.issuance = issuance_reader or PermitIssuanceContextReader()
        self.auth = authorization
        self.storage = object_storage
