"""CertificateAccessLogsRepository — permit.certificate_access_logs 寫入。"""

from __future__ import annotations

from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.permit_document.infra.repositories._orm_detach import detach_optional
from src.contexts.permit_document.infra.schema.certificate_access_logs import CertificateAccessLogs


class CertificateAccessLogsRepository:
    def add(self, row: CertificateAccessLogs) -> CertificateAccessLogs:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
