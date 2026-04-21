"""
Permit — 許可證聚合根（對應 permit.permits 及其子集合 documents / jobs 之叢集）。

責任：
- 維護 **僅核准申請** 始得建立（由呼叫端傳入 `application_approved` 佐證，Domain 不查 DB）。
- 維護 **最終路線綁定**（`FinalRouteBinding`）。
- 維護聚合狀態：待產檔、已核發、已核發但待補產文件。
- 協調子實體：`PermitDocument`（版本／SUPERSEDED）、`DocumentGenerationJob`（工作狀態機）。
- 由子實體計算 **DocumentBundle**（三類 PDF 之最新 ACTIVE **DocumentRef**）。

對照規格 8.1：**selected route ref** 以 **`FinalRouteBinding`**（selected_candidate_id／override_id）表達；
**DocumentBundle** 不為單獨持久化欄位，而由 **`build_document_bundle()`** 自 **documents** 子實體導出之值物件視圖。

本類別 **不** 依賴 Infra / App / API；核准事實與路線資料由 App 層讀取他 context 後傳入。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.contexts.permit_document.domain.entities.document_job import DocumentGenerationJob
from src.contexts.permit_document.domain.entities.permit_document import (
    PENDING_FILE_ID_PLACEHOLDER,
    PermitDocument,
)
from src.contexts.permit_document.domain.errors import (
    InvalidPermitStateError,
    PermitCreationPreconditionError,
)
from src.contexts.permit_document.domain.value_objects import (
    DocumentBundle,
    DocumentRef,
    DocumentTypeCodePhase,
    FinalRouteBinding,
    PermitStatus,
    PermitStatusPhase,
    PermitApprovedPeriod,
    PermitDocumentRecordStatus,
    PermitDocumentRecordStatusPhase,
    PermitNo,
    RouteSummaryText,
)


@dataclass
class Permit:
    """
    許可證聚合根。

    責任欄位（對應 `permit.permits` 與規格 8.1）：
    permit_id, permit_no, application_id, **status**（值物件 **PermitStatus**）、
    approved_period（approved_start_at／approved_end_at）、route_binding、route_summary、
    note、issued_at、時間戳；並內聚 **documents** / **jobs** 兩個子集合（執行期由 App 載入或逐步附加）。
    """

    permit_id: UUID
    permit_no: PermitNo
    application_id: UUID
    status: PermitStatus
    approved_period: PermitApprovedPeriod
    route_binding: FinalRouteBinding
    route_summary: RouteSummaryText
    note: str | None
    issued_at: datetime | None
    created_at: datetime
    updated_at: datetime
    documents: list[PermitDocument] = field(default_factory=list)
    jobs: list[DocumentGenerationJob] = field(default_factory=list)

    @classmethod
    def create_for_approved_application(
        cls,
        *,
        permit_id: UUID,
        permit_no: PermitNo,
        application_id: UUID,
        application_approved: bool,
        approved_period: PermitApprovedPeriod,
        route_binding: FinalRouteBinding,
        route_summary: RouteSummaryText,
        note: str | None,
        now: datetime,
    ) -> Permit:
        """
        UC-PERMIT-01：因 **ApplicationApproved**（或同等語意）建立 Permit。

        責任：
        - 驗證 **僅核准案** 可建證（`application_approved` 必須為 True）。
        - `route_binding` 已內含「至少一則路線參照」檢查。
        - 初始狀態 **pending_generation**（§8）；**issued_at** 為 None；子集合為空（文件列與 jobs 由後續方法附加）。
        """
        if not application_approved:
            raise PermitCreationPreconditionError(
                "only an approved application may create a permit (application_approved is False)"
            )
        return cls(
            permit_id=permit_id,
            permit_no=permit_no,
            application_id=application_id,
            status=PermitStatus.pending_generation(),
            approved_period=approved_period,
            route_binding=route_binding,
            route_summary=route_summary,
            note=note,
            issued_at=None,
            created_at=now,
            updated_at=now,
            documents=[],
            jobs=[],
        )

    def attach_generation_job(self, job: DocumentGenerationJob, now: datetime) -> None:
        """
        將新產檔工作單納入本聚合（UC-PERMIT-01 建立 jobs）。

        責任：檢查 **job.application_id** 與本 permit 一致；**permit_id** 若填則須等於本聚合 id。
        """
        if job.application_id != self.application_id:
            raise InvalidPermitStateError(
                "job.application_id must match permit.application_id",
                details={
                    "permit_application_id": str(self.application_id),
                    "job_application_id": str(job.application_id),
                },
            )
        if job.permit_id is not None and job.permit_id != self.permit_id:
            raise InvalidPermitStateError(
                "job.permit_id must match permit_id when set",
                details={"permit_id": str(self.permit_id), "job_permit_id": str(job.permit_id)},
            )
        self.jobs.append(job)
        self._touch(now)

    def register_pending_document(
        self,
        *,
        document_id: UUID,
        document_type: str,
        template_code: str,
        version_no: int,
        now: datetime,
    ) -> PermitDocument:
        """
        登記一筆待產製文件列（PENDING，file_id 使用佔位）。

        責任：**version_no** 須 >=1；同類型若已有 ACTIVE，應先呼叫 `begin_regeneration` 將其 SUPERSEDED。
        """
        if version_no < 1:
            raise InvalidPermitStateError(
                "version_no must be >= 1",
                details={"document_type": document_type, "version_no": version_no},
            )
        row = PermitDocument(
            document_id=document_id,
            permit_id=self.permit_id,
            application_id=self.application_id,
            document_type=document_type.strip(),
            file_id=PENDING_FILE_ID_PLACEHOLDER,
            template_code=template_code.strip(),
            version_no=version_no,
            status=PermitDocumentRecordStatus.pending(),
            created_at=now,
            updated_at=now,
        )
        self.documents.append(row)
        self._touch(now)
        return row

    def begin_regeneration(
        self,
        *,
        document_type: str,
        new_document_id: UUID,
        template_code: str,
        now: datetime,
    ) -> PermitDocument:
        """
        文件重產：將目前 **ACTIVE** 之該類型標為 SUPERSEDED，並新增 **PENDING** 列（版本 +1）。

        責任：落實「文件重產需保留版本」；若無 ACTIVE 則視為首次建列（版本 1）。
        """
        dtype = document_type.strip()
        active = self._latest_document_for_type(dtype, active_only=True)
        if active is not None:
            active.mark_superseded(now)
            next_version = max(d.version_no for d in self.documents if d.document_type == dtype) + 1
        else:
            next_version = 1
        return self.register_pending_document(
            document_id=new_document_id,
            document_type=dtype,
            template_code=template_code,
            version_no=next_version,
            now=now,
        )

    def mark_fully_issued(self, now: datetime) -> None:
        """
        必要文件皆已 ACTIVE 且 App 判定可核發時，轉為 **ISSUED** 並填 **issued_at**。

        責任：僅允許自 **pending_generation** 轉移；若 bundle 仍缺任一標準類型之 ACTIVE，拒絕。
        """
        if self.status.value != PermitStatusPhase.PENDING_GENERATION.value:
            raise InvalidPermitStateError(
                "mark_fully_issued only allowed from pending_generation",
                current_status=self.status.value,
            )
        bundle = self.build_document_bundle()
        if bundle.permit_pdf is None or bundle.route_map_pdf is None or bundle.decision_pdf is None:
            raise InvalidPermitStateError(
                "cannot mark issued: permit_pdf, route_map_pdf, and decision_pdf must all be ACTIVE",
                details={
                    "has_permit_pdf": bundle.permit_pdf is not None,
                    "has_route_map": bundle.route_map_pdf is not None,
                    "has_decision_pdf": bundle.decision_pdf is not None,
                },
            )
        self.status = PermitStatus.issued()
        self.issued_at = now
        self._touch(now)

    def mark_document_regeneration_required(self, now: datetime) -> None:
        """
        產檔失敗等情境：**不回滾核准**，但若已 **ISSUED** 則標示 **待補產**。

        責任：
        - 自 **ISSUED** → **ISSUED_WITH_PENDING_DOCUMENT_REGEN**。
        - 若仍在 **pending_generation**，維持不變（失敗由 FAILED 列／job 表達）。
        - 已為 **ISSUED_WITH_PENDING_DOCUMENT_REGEN** 則冪等不重拋。
        """
        phase = PermitStatusPhase
        if self.status.value == phase.ISSUED.value:
            self.status = PermitStatus.issued_with_pending_document_regen()
            self._touch(now)
        elif self.status.value == phase.ISSUED_WITH_PENDING_DOCUMENT_REGEN.value:
            self._touch(now)
        elif self.status.value == phase.PENDING_GENERATION.value:
            self._touch(now)
        else:
            raise InvalidPermitStateError(
                "unexpected permit status for mark_document_regeneration_required",
                current_status=self.status.value,
            )

    def clear_document_regeneration_flag_if_resolved(self, now: datetime) -> None:
        """
        待補產文件皆已恢復（三類 ACTIVE）時，自 **ISSUED_WITH_PENDING_DOCUMENT_REGEN** 回到 **ISSUED**。

        責任：若 bundle 不完整則拒絕。
        """
        if self.status.value != PermitStatusPhase.ISSUED_WITH_PENDING_DOCUMENT_REGEN.value:
            raise InvalidPermitStateError(
                "clear_document_regeneration_flag only when issued_pending_document_regen",
                current_status=self.status.value,
            )
        bundle = self.build_document_bundle()
        if bundle.permit_pdf is None or bundle.route_map_pdf is None or bundle.decision_pdf is None:
            raise InvalidPermitStateError(
                "cannot clear regen flag until all standard documents are ACTIVE again",
            )
        self.status = PermitStatus.issued()
        self._touch(now)

    def build_document_bundle(self) -> DocumentBundle:
        """
        由子實體集合計算三類文件之「目前有效」**DocumentRef**（各取 **ACTIVE** 中版本號最大者）。

        責任：純查詢、不修改狀態；供 UC-PERMIT-03 與核發檢查使用。
        """

        active = PermitDocumentRecordStatusPhase.ACTIVE.value

        def pick_ref(phase: DocumentTypeCodePhase) -> DocumentRef | None:
            candidates = [
                d
                for d in self.documents
                if d.document_type == phase.value
                and d.status.value == active
                and d.file_id != PENDING_FILE_ID_PLACEHOLDER
            ]
            if not candidates:
                return None
            best = max(candidates, key=lambda x: x.version_no)
            return DocumentRef(
                document_id=best.document_id,
                file_id=best.file_id,
                document_type=best.document_type,
                version_no=best.version_no,
            )

        permit_main = pick_ref(DocumentTypeCodePhase.PERMIT_PDF) or pick_ref(
            DocumentTypeCodePhase.PERMIT_CERTIFICATE_PDF
        )
        return DocumentBundle(
            permit_pdf=permit_main,
            route_map_pdf=pick_ref(DocumentTypeCodePhase.ROUTE_MAP_PDF),
            decision_pdf=pick_ref(DocumentTypeCodePhase.DECISION_PDF),
        )

    def _latest_document_for_type(
        self,
        document_type: str,
        *,
        active_only: bool,
    ) -> PermitDocument | None:
        pool = [d for d in self.documents if d.document_type == document_type]
        if active_only:
            pool = [
                d
                for d in pool
                if d.status.value == PermitDocumentRecordStatusPhase.ACTIVE.value
            ]
        if not pool:
            return None
        return max(pool, key=lambda d: d.version_no)

    def _touch(self, now: datetime) -> None:
        self.updated_at = now
