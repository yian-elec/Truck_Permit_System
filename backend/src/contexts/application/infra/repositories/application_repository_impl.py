"""
ApplicationRepository 之 SQLAlchemy 實作。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session，不自行建立引擎／連線。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.application.domain.entities import Application
from src.contexts.application.domain.repositories import ApplicationRepository
from src.contexts.application.infra.schema import (
    ApplicantProfiles,
    Applications,
    Attachments,
    Checklists,
    CompanyProfiles,
    StatusHistories,
    StoredFiles,
    Vehicles,
)

from ._mappers import (
    applicant_row_from_profile,
    applications_row_from_aggregate,
    checklist_row_from_item,
    company_row_from_profile,
    history_row_from_entry,
    rows_to_aggregate,
    vehicle_row_from_entity,
)


class ApplicationRepositoryImpl(ApplicationRepository):
    """
    將 Application 聚合載入／儲存至 `application` schema。

    責任：
    - `get_by_id`／`get_by_application_no`： eager 載入子表並映射為領域聚合
    - `save`：同步主表、申請人／公司、車輛、檢核清單、狀態歷程；**attachments** 列由
      `persist_attachment_upload`／外部流程寫入，一般 `save` 不刪除既有附件列。
    - `persist_attachment_upload`：於單一交易中寫入 `ops.stored_files` 與 `application.attachments`，
      並重算檢核清單後一併 save 聚合其餘部分。
    """

    def get_by_id(self, application_id: UUID) -> Application | None:
        with get_session() as session:
            row = session.query(Applications).filter_by(application_id=application_id).first()
            if row is None:
                return None
            return self._hydrate(session, row)

    def get_by_application_no(self, application_no: str) -> Application | None:
        with get_session() as session:
            row = session.query(Applications).filter_by(application_no=application_no).first()
            if row is None:
                return None
            return self._hydrate(session, row)

    def _hydrate(self, session: Session, app_row: Applications) -> Application:
        aid = app_row.application_id
        applicant = session.query(ApplicantProfiles).filter_by(application_id=aid).first()
        company = session.query(CompanyProfiles).filter_by(application_id=aid).first()
        vehicles = session.query(Vehicles).filter_by(application_id=aid).all()
        checklists = session.query(Checklists).filter_by(application_id=aid).all()
        attachments = session.query(Attachments).filter_by(application_id=aid).all()
        histories = session.query(StatusHistories).filter_by(application_id=aid).all()
        app = rows_to_aggregate(
            app_row,
            applicant,
            company,
            vehicles,
            checklists,
            attachments,
            histories,
        )
        app.attachment_bundle.align_checklist_after_load_from_db()
        return app

    def save(self, application: Application) -> None:
        now = datetime.now(timezone.utc)
        with get_session() as session:
            try:
                self._save_aggregate(session, application, now)
            except Exception:
                session.rollback()
                logger.db_error(
                    f"Application save failed application_id={application.application_id}"
                )
                raise

    def _save_aggregate(self, session: Session, application: Application, now: datetime) -> None:
        """
        於既有 Session 內寫回聚合（不含新增附件列；附件請先 merge 再 hydrate 後呼叫）。

        責任：供 `save` 與 `persist_attachment_upload` 共用，維持單一交易語意。
        """
        aid = application.application_id
        main = applications_row_from_aggregate(application, updated_at=now)
        session.merge(main)

        session.query(ApplicantProfiles).filter_by(application_id=aid).delete(
            synchronize_session=False
        )
        if application.applicant_profile:
            session.merge(
                applicant_row_from_profile(application.applicant_profile, updated_at=now)
            )

        session.query(CompanyProfiles).filter_by(application_id=aid).delete(
            synchronize_session=False
        )
        if application.company_profile:
            session.merge(
                company_row_from_profile(application.company_profile, updated_at=now)
            )

        keep_vehicle_ids = {v.vehicle_id for v in application.vehicles}
        q_del = session.query(Vehicles).filter(Vehicles.application_id == aid)
        if keep_vehicle_ids:
            q_del = q_del.filter(~Vehicles.vehicle_id.in_(keep_vehicle_ids))
        q_del.delete(synchronize_session=False)
        for v in application.vehicles:
            session.merge(vehicle_row_from_entity(v, updated_at=now))

        session.query(Checklists).filter_by(application_id=aid).delete(synchronize_session=False)
        for item in application.attachment_bundle.checklist_items:
            session.add(checklist_row_from_item(aid, item, now=now))

        existing_hist_ids = {
            h.history_id
            for h in session.query(StatusHistories).filter_by(application_id=aid).all()
        }
        for h in application.status_histories:
            if h.history_id not in existing_hist_ids:
                session.add(history_row_from_entry(h))

        logger.db_info(f"Application saved application_id={aid} version={application.version}")

    def persist_attachment_upload(
        self,
        *,
        application_id: UUID,
        attachment_id: UUID,
        file_id: UUID,
        attachment_type: str,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        checksum_sha256: str,
        status: str,
        ocr_status: str,
        uploaded_by: UUID | None,
        uploaded_at: datetime,
        bucket_name: str,
        object_key: str,
        storage_provider: str,
        virus_scan_status: str,
    ) -> Application:
        """
        UC-APP-04：寫入 stored_files 與 attachments，並重算檢核清單後保存聚合。

        責任：單一資料庫交易內完成，避免附件列已存在但 checklist 未更新之不一致。
        """
        now = datetime.now(timezone.utc)
        with get_session() as session:
            try:
                session.merge(
                    StoredFiles(
                        file_id=file_id,
                        bucket_name=bucket_name,
                        object_key=object_key,
                        storage_provider=storage_provider,
                        mime_type=mime_type,
                        size_bytes=size_bytes,
                        checksum_sha256=checksum_sha256,
                        virus_scan_status=virus_scan_status,
                        created_at=now,
                    )
                )
                session.merge(
                    Attachments(
                        attachment_id=attachment_id,
                        application_id=application_id,
                        attachment_type=attachment_type,
                        file_id=file_id,
                        original_filename=original_filename,
                        mime_type=mime_type,
                        size_bytes=size_bytes,
                        checksum_sha256=checksum_sha256,
                        status=status,
                        ocr_status=ocr_status,
                        uploaded_by=uploaded_by,
                        uploaded_at=uploaded_at,
                        created_at=now,
                        updated_at=now,
                    )
                )
                session.flush()
                app_row = (
                    session.query(Applications).filter_by(application_id=application_id).first()
                )
                if app_row is None:
                    raise LookupError(f"application not found: {application_id}")
                app = self._hydrate(session, app_row)
                app.reconcile_attachment_checklist_after_db_upload(now)
                self._save_aggregate(session, app, now)
                return app
            except Exception:
                session.rollback()
                logger.db_error(
                    f"persist_attachment_upload failed application_id={application_id} "
                    f"attachment_id={attachment_id}"
                )
                raise

    def delete_attachment_and_reconcile(
        self,
        *,
        application_id: UUID,
        attachment_id: UUID,
    ) -> Application:
        """
        刪除附件列與對應 stored_files，並重算檢核清單後保存。

        責任：供申請人刪除已上傳附件 API 使用；假設 file_id 僅由此附件引用。
        """
        now = datetime.now(timezone.utc)
        with get_session() as session:
            try:
                row = (
                    session.query(Attachments)
                    .filter_by(application_id=application_id, attachment_id=attachment_id)
                    .first()
                )
                if row is None:
                    raise LookupError(
                        f"attachment not found: application_id={application_id} "
                        f"attachment_id={attachment_id}"
                    )
                fid = row.file_id
                session.delete(row)
                session.flush()
                sf = session.query(StoredFiles).filter_by(file_id=fid).first()
                if sf is not None:
                    session.delete(sf)
                session.flush()
                app_row = (
                    session.query(Applications).filter_by(application_id=application_id).first()
                )
                if app_row is None:
                    raise LookupError(f"application not found: {application_id}")
                app = self._hydrate(session, app_row)
                app.reconcile_attachment_checklist_after_db_upload(now)
                self._save_aggregate(session, app, now)
                return app
            except Exception:
                session.rollback()
                logger.db_error(
                    f"delete_attachment_and_reconcile failed application_id={application_id} "
                    f"attachment_id={attachment_id}"
                )
                raise
