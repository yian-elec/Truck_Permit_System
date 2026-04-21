"""
DocumentsRepository — permit.documents 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session。
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import desc, select

from shared.core.db.connection import get_session

from src.contexts.permit_document.infra.repositories._orm_detach import detach_all, detach_optional
from src.contexts.permit_document.infra.schema.documents import Documents


class DocumentsRepository:
    """許可文件列存取。"""

    def get_by_id(self, document_id: UUID) -> Documents | None:
        with get_session() as session:
            row = session.get(Documents, document_id)
            return detach_optional(session, row)

    def get_by_file_id(self, file_id: UUID) -> Documents | None:
        """依 **file_id** 查單一文件列（簽名下載補寫磁碟時使用）。"""
        with get_session() as session:
            row = session.scalars(
                select(Documents).where(Documents.file_id == file_id).limit(1)
            ).first()
            return detach_optional(session, row)

    def list_by_permit_id(self, permit_id: UUID) -> List[Documents]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(Documents).where(Documents.permit_id == permit_id)
                ).all()
            )
            return detach_all(session, rows)

    def list_by_application_id(self, application_id: UUID) -> List[Documents]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(Documents).where(Documents.application_id == application_id)
                ).all()
            )
            return detach_all(session, rows)

    def get_latest_by_permit_id(self, permit_id: UUID) -> Documents | None:
        """每許可單一 **is_latest** 列（§8 單證）；若無則退回 **version_no** 最大列（相容舊資料）。"""
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(Documents)
                    .where(Documents.permit_id == permit_id)
                    .where(Documents.is_latest.is_(True))
                    .limit(1)
                ).all()
            )
            if rows:
                return detach_optional(session, rows[0])
            fallback = session.scalars(
                select(Documents)
                .where(Documents.permit_id == permit_id)
                .order_by(desc(Documents.version_no))
                .limit(1)
            ).first()
            return detach_optional(session, fallback)

    def add(self, row: Documents) -> Documents:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def merge_update(self, row: Documents) -> Documents | None:
        with get_session() as session:
            existing = session.get(Documents, row.document_id)
            if existing is None:
                return None
            existing.permit_id = row.permit_id
            existing.application_id = row.application_id
            existing.document_type = row.document_type
            existing.file_id = row.file_id
            existing.template_code = row.template_code
            existing.version_no = row.version_no
            existing.status = row.status
            existing.is_latest = row.is_latest
            existing.checksum_sha256 = row.checksum_sha256
            existing.generated_at = row.generated_at
            existing.error_message = row.error_message
            existing.updated_at = row.updated_at
            session.flush()
            session.refresh(existing)
            return detach_optional(session, existing)
