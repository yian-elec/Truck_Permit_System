"""
申請案件聚合根（Application aggregate root）。

責任：
- 維護 application_no、狀態、申請區間、送達方式、申請人與公司資料、車輛、附件檢核之一致性
- 實作核心規則：草稿可編輯、已送件不可直接覆寫核心、補件狀態可走補件編輯、必備附件與至少一車、期間不超過政策上限、狀態歷程僅附加

外部依賴（政策天數上限等）由方法參數注入，不引用 Infra。路線需求由申請人於草稿儲存、自動規劃由審查端執行，送件閘道不檢查 routing.route_requests。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from .applicant_profile import ApplicantProfile
from .attachment_bundle import AttachmentBundle
from .attachment_descriptor import AttachmentDescriptor
from .checklist_item import ChecklistItem
from .company_profile import CompanyProfile
from .status_history_entry import StatusHistoryEntry
from .submission_readiness import SubmissionReadiness
from .vehicle import Vehicle
from ..errors import (
    ConsentRequiredError,
    CoreDataNotEditableError,
    InvalidApplicationStateError,
    InvalidDomainValueError,
    SubmissionRequirementsNotMetError,
    VehicleLimitExceededError,
)
from ..value_objects import (
    ApplicantType,
    ApplicationStatus,
    ApplicationStatusPhase,
    DeliveryMethod,
    PermitPeriod,
    ReasonType,
    SourceChannel,
    VehiclePlate,
)

# 單一案件可綁定車輛之上限（政策可改時可改為由建構子注入）
MAX_VEHICLES_PER_APPLICATION = 50


@dataclass
class Application:
    """
    重型貨車通行證「申請案件」聚合根。

    責任：對外邊界為此類別之公開方法；內部集合（車輛、歷史、附件組）不應被外部直接篡改，
    應透過聚合方法以維持不變條件。
    """

    application_id: UUID
    application_no: str
    status: ApplicationStatus
    applicant_type: ApplicantType
    reason_type: ReasonType
    reason_detail: str | None
    requested_period: PermitPeriod
    delivery_method: DeliveryMethod
    source_channel: SourceChannel
    applicant_user_id: UUID | None
    consent_accepted_at: datetime | None
    submitted_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
    applicant_profile: ApplicantProfile | None
    company_profile: CompanyProfile | None
    vehicles: list[Vehicle] = field(default_factory=list)
    attachment_bundle: AttachmentBundle = field(default_factory=lambda: AttachmentBundle.empty())
    status_histories: list[StatusHistoryEntry] = field(default_factory=list)

    # ------------------------------------------------------------------
    # 建立
    # ------------------------------------------------------------------

    @classmethod
    def open_draft(
        cls,
        *,
        application_id: UUID,
        application_no: str,
        applicant_user_id: UUID | None,
        applicant_type: ApplicantType,
        reason_type: ReasonType,
        reason_detail: str | None,
        requested_period: PermitPeriod,
        delivery_method: DeliveryMethod,
        source_channel: SourceChannel,
        now: datetime,
    ) -> Application:
        """
        開立新草稿案件（UC-APP-01 領域部分）。

        責任：產生 status=draft、version=1；checklist 須由 App 呼叫 replace_checklist 初始化。
        application_no 由 App／序號服務產生後傳入。
        """
        return cls(
            application_id=application_id,
            application_no=application_no,
            status=ApplicationStatus.draft(),
            applicant_type=applicant_type,
            reason_type=reason_type,
            reason_detail=reason_detail,
            requested_period=requested_period,
            delivery_method=delivery_method,
            source_channel=source_channel,
            applicant_user_id=applicant_user_id,
            consent_accepted_at=None,
            submitted_at=None,
            version=1,
            created_at=now,
            updated_at=now,
            applicant_profile=None,
            company_profile=None,
            vehicles=[],
            attachment_bundle=AttachmentBundle.empty(),
            status_histories=[],
        )

    # ------------------------------------------------------------------
    # 內部：可編輯性
    # ------------------------------------------------------------------

    def _assert_may_mutate_case_content(self) -> None:
        """
        是否允許變更案件內容（欄位、車輛、附件組合等）。

        責任：草稿可全量編輯；補件狀態允許依監理要求修正／補傳；已送件與補件回覆後待審狀態鎖住直接編輯。
        """
        if self.status.allows_full_draft_editing():
            return
        if self.status.is_supplement_required():
            return
        raise CoreDataNotEditableError(
            "Core application data cannot be edited in the current status",
            current_status=self.status.value,
        )

    # ------------------------------------------------------------------
    # UC-APP-02：更新草稿（或補件下）之申請主體欄位
    # ------------------------------------------------------------------

    def update_application_core(
        self,
        *,
        reason_type: ReasonType | None = None,
        reason_detail: str | None = None,
        requested_period: PermitPeriod | None = None,
        delivery_method: DeliveryMethod | None = None,
        now: datetime,
    ) -> None:
        """
        更新申請主表核心欄位（事由、期間、送達方式等）。

        責任：驗證目前狀態允許編輯；若傳入新期間，仍須於送件時由政策天數複驗。
        """
        self._assert_may_mutate_case_content()
        if reason_type is not None:
            self.reason_type = reason_type
        if reason_detail is not None:
            self.reason_detail = reason_detail
        if requested_period is not None:
            self.requested_period = requested_period
        if delivery_method is not None:
            self.delivery_method = delivery_method
        self._bump_version_and_touch(now)

    def replace_applicant_profile(self, profile: ApplicantProfile, now: datetime) -> None:
        """整體取代自然人申請人資料區塊。"""
        self._assert_may_mutate_case_content()
        self.applicant_profile = profile
        self._bump_version_and_touch(now)

    def replace_company_profile(self, profile: CompanyProfile, now: datetime) -> None:
        """整體取代公司申請人資料區塊。"""
        self._assert_may_mutate_case_content()
        self.company_profile = profile
        self._bump_version_and_touch(now)

    def initialize_checklist(self, items: list[ChecklistItem], now: datetime) -> None:
        """
        由 App 依服務公版建立檢核清單。

        責任：僅在草稿或補件允許編輯時呼叫；會覆寫既有清單列（歷史另存於 status_histories／稽核由 App 處理）。
        """
        self._assert_may_mutate_case_content()
        self.attachment_bundle.replace_checklist(list(items))
        self._bump_version_and_touch(now)

    # ------------------------------------------------------------------
    # UC-APP-03：車輛
    # ------------------------------------------------------------------

    def add_vehicle(
        self,
        *,
        plate_no: VehiclePlate,
        vehicle_kind: str,
        gross_weight_ton: Decimal | None,
        license_valid_until: date | None,
        trailer_plate_no: VehiclePlate | None,
        now: datetime,
        vehicle_id: UUID | None = None,
    ) -> Vehicle:
        """
        新增車輛；若為第一輛自動設為 primary。

        責任：檢查數量上限；同一聚合內僅一輛 primary。
        """
        self._assert_may_mutate_case_content()
        if len(self.vehicles) >= MAX_VEHICLES_PER_APPLICATION:
            raise VehicleLimitExceededError(
                f"Cannot add more than {MAX_VEHICLES_PER_APPLICATION} vehicles per application",
            )
        is_primary = len(self.vehicles) == 0
        v = Vehicle.create(
            application_id=self.application_id,
            plate_no=plate_no,
            vehicle_kind=vehicle_kind,
            gross_weight_ton=gross_weight_ton,
            license_valid_until=license_valid_until,
            trailer_plate_no=trailer_plate_no,
            is_primary=is_primary,
            now=now,
            vehicle_id=vehicle_id,
        )
        self.vehicles.append(v)
        self._bump_version_and_touch(now)
        return v

    def remove_vehicle(self, vehicle_id: UUID, now: datetime) -> None:
        """移除車輛；若刪除主車則將剩餘第一輛升為主車。"""
        self._assert_may_mutate_case_content()
        before = len(self.vehicles)
        self.vehicles = [x for x in self.vehicles if x.vehicle_id != vehicle_id]
        if len(self.vehicles) == before:
            raise InvalidApplicationStateError(
                "Vehicle not found on this application",
                details={"vehicle_id": str(vehicle_id)},
            )
        self._ensure_single_primary()
        self._bump_version_and_touch(now)

    def update_vehicle(
        self,
        vehicle_id: UUID,
        *,
        plate_no: VehiclePlate | None = None,
        vehicle_kind: str | None = None,
        gross_weight_ton: Decimal | None = None,
        license_valid_until: date | None = None,
        trailer_plate_no: VehiclePlate | None = None,
        now: datetime,
    ) -> None:
        """更新單一車輛欄位（部分更新以 replace 實作）。"""
        self._assert_may_mutate_case_content()
        idx = next((i for i, v in enumerate(self.vehicles) if v.vehicle_id == vehicle_id), None)
        if idx is None:
            raise InvalidApplicationStateError(
                "Vehicle not found on this application",
                details={"vehicle_id": str(vehicle_id)},
            )
        v = self.vehicles[idx]
        new_plate = plate_no if plate_no is not None else v.plate_no
        new_kind = vehicle_kind if vehicle_kind is not None else v.vehicle_kind
        new_weight = gross_weight_ton if gross_weight_ton is not None else v.gross_weight_ton
        new_license = license_valid_until if license_valid_until is not None else v.license_valid_until
        new_trailer = trailer_plate_no if trailer_plate_no is not None else v.trailer_plate_no
        updated = Vehicle(
            vehicle_id=v.vehicle_id,
            application_id=v.application_id,
            plate_no=new_plate,
            vehicle_kind=new_kind,
            gross_weight_ton=new_weight,
            license_valid_until=new_license,
            trailer_plate_no=new_trailer,
            is_primary=v.is_primary,
            created_at=v.created_at,
            updated_at=now,
        )
        self.vehicles[idx] = updated
        self._bump_version_and_touch(now)

    def _ensure_single_primary(self) -> None:
        """確保恰有一輛主車（若仍有車輛）。"""
        if not self.vehicles:
            return
        primaries = [v for v in self.vehicles if v.is_primary]
        if len(primaries) == 1:
            return
        if len(primaries) == 0:
            self.vehicles[0].mark_primary()
            for v in self.vehicles[1:]:
                v.mark_secondary()
            return
        # 多於一輛 primary：保留第一輛
        first = True
        for v in self.vehicles:
            if v.is_primary:
                if first:
                    first = False
                else:
                    v.mark_secondary()

    # ------------------------------------------------------------------
    # UC-APP-04：附件（領域層僅登記描述與檢核聯動）
    # ------------------------------------------------------------------

    def register_uploaded_attachment(self, descriptor: AttachmentDescriptor, now: datetime) -> None:
        """
        附件已成功寫入 storage 並建立 persistence 列之後，於領域登記。

        責任：更新 AttachmentBundle 並勾選對應 checklist；病毒掃描／OCR 由其他 context 處理，
        若需「掃描通過才算 uploaded」由 App 在呼叫本方法前把 descriptor.status 設好。
        """
        self._assert_may_mutate_case_content()
        self.attachment_bundle.register_uploaded_attachment(descriptor)
        self._bump_version_and_touch(now)

    def remove_attachment_reference(self, attachment_id: UUID, now: datetime) -> None:
        """移除附件參考並重算檢核滿足狀態。"""
        self._assert_may_mutate_case_content()
        self.attachment_bundle.remove_attachment_reference(attachment_id)
        self._bump_version_and_touch(now)

    def reconcile_attachment_checklist_after_db_upload(self, now: datetime) -> None:
        """
        於資料庫已寫入／刪除附件列後，重算檢核清單並遞增版本。

        責任：UC-APP-04 完成寫入 storage 與 attachments 表後，由 App 載入聚合並呼叫，
        使 checklist 與實際已上傳且狀態為完成之附件一致。
        """
        self._assert_may_mutate_case_content()
        self.attachment_bundle.reconcile_checklist_with_current_uploads()
        self._bump_version_and_touch(now)

    # ------------------------------------------------------------------
    # 同意條款
    # ------------------------------------------------------------------

    def record_consent_accepted(self, now: datetime) -> None:
        """使用者已閱讀並同意最新版條款之領域事實。"""
        self._assert_may_mutate_case_content()
        self.consent_accepted_at = now
        self._bump_version_and_touch(now)

    # ------------------------------------------------------------------
    # UC-APP-05：送件前檢查
    # ------------------------------------------------------------------

    def evaluate_submission_readiness(
        self,
        *,
        max_permit_calendar_days: int,
    ) -> SubmissionReadiness:
        """
        彙整是否可送件與缺漏代碼。

        責任：不重複拋錯，供 API 組裝說明；實際送件仍應呼叫 submit 內之 assert。
        """
        missing: list[str] = []
        if not self._profile_complete():
            missing.append("incomplete_profile")
        if not self.consent_accepted_at:
            missing.append("missing_consent")
        if len(self.vehicles) < 1:
            missing.append("missing_vehicles")
        if not self.attachment_bundle.all_required_satisfied():
            missing.append("missing_required_attachments")
        try:
            self.requested_period.assert_within_max_calendar_days(max_permit_calendar_days)
        except InvalidDomainValueError:
            missing.append("permit_period_exceeds_policy")
        can = len(missing) == 0
        return SubmissionReadiness(can_submit=can, missing_reason_codes=tuple(missing))

    def _profile_complete(self) -> bool:
        """依 applicant_type 檢查自然人或公司主體最低欄位。"""
        t = self.applicant_type
        if t.is_natural_person():
            return bool(
                self.applicant_profile
                and self.applicant_profile.minimum_complete_for_natural_person()
            )
        if t.is_company():
            return bool(
                self.company_profile and self.company_profile.minimum_complete_for_company()
            )
        ap = self.applicant_profile
        cp = self.company_profile
        if ap and ap.minimum_complete_for_natural_person():
            return True
        if cp and cp.minimum_complete_for_company():
            return True
        return False

    def assert_ready_to_submit(
        self,
        *,
        max_permit_calendar_days: int,
    ) -> None:
        """
        送件前強制檢查；不通過則拋出領域例外。

        責任：UC-APP-06 第一步應呼叫本方法。
        """
        r = self.evaluate_submission_readiness(
            max_permit_calendar_days=max_permit_calendar_days,
        )
        if r.can_submit:
            return
        codes = list(r.missing_reason_codes)
        if "missing_consent" in codes:
            raise ConsentRequiredError(
                "Consent must be accepted before submission",
                missing_reason_codes=codes,
            )
        raise SubmissionRequirementsNotMetError(
            "Submission requirements are not met",
            missing_reason_codes=codes,
        )

    # ------------------------------------------------------------------
    # UC-APP-06：送件
    # ------------------------------------------------------------------

    def submit(
        self,
        *,
        now: datetime,
        changed_by: UUID | None,
        max_permit_calendar_days: int,
        history_id: UUID | None = None,
    ) -> None:
        """
        首次送件：draft → submitted。

        責任：執行完整檢查、寫入 submitted_at、附加狀態歷史。
        """
        if not self.status.is_draft():
            raise InvalidApplicationStateError(
                "Only draft applications can be submitted for the first time",
                current_status=self.status.value,
            )
        self.assert_ready_to_submit(
            max_permit_calendar_days=max_permit_calendar_days,
        )
        self.apply_status_transition(
            to_status=ApplicationStatus.submitted(),
            now=now,
            changed_by=changed_by,
            reason="Applicant submitted application",
            history_id=history_id,
        )
        self.submitted_at = now
        self._bump_version_and_touch(now)

    # ------------------------------------------------------------------
    # 補件：進入補件／回覆補件（UC-APP-07 領域骨架）
    # ------------------------------------------------------------------

    def enter_supplement_required(
        self,
        *,
        now: datetime,
        changed_by: UUID | None,
        reason: str | None,
        history_id: UUID | None = None,
    ) -> None:
        """
        審查方要求補件時之狀態轉移（通常由審查 context 觸發，App 呼叫）。

        責任：由已送件相關狀態進入 supplement_required；歷史附加於本聚合。
        """
        allowed_from = {
            ApplicationStatusPhase.SUBMITTED.value,
            ApplicationStatusPhase.UNDER_REVIEW.value,
            ApplicationStatusPhase.RESUBMITTED.value,
        }
        if self.status.value not in allowed_from:
            raise InvalidApplicationStateError(
                "Cannot request supplement from the current status",
                current_status=self.status.value,
            )
        self.apply_status_transition(
            to_status=ApplicationStatus.supplement_required(),
            now=now,
            changed_by=changed_by,
            reason=reason or "Supplement required",
            history_id=history_id,
        )
        self._bump_version_and_touch(now)

    def finalize_supplement_response(
        self,
        *,
        now: datetime,
        changed_by: UUID | None,
        history_id: UUID | None = None,
    ) -> None:
        """
        申請人完成補件上傳／可編欄位修正後，將案件標示為再次送出待審。

        責任：具體「補件項目是否已滿足」可由 App 先查後呼叫；此處僅處理狀態與歷史。
        """
        if not self.status.is_supplement_required():
            raise InvalidApplicationStateError(
                "Supplement response is only allowed when status is supplement_required",
                current_status=self.status.value,
            )
        self.apply_status_transition(
            to_status=ApplicationStatus.resubmitted(),
            now=now,
            changed_by=changed_by,
            reason="Applicant responded to supplement request",
            history_id=history_id,
        )
        self._bump_version_and_touch(now)

    # ------------------------------------------------------------------
    # 審查結案（由 Review_Decision context 之 App 服務觸發）
    # ------------------------------------------------------------------

    def approve_by_officer(
        self,
        *,
        now: datetime,
        changed_by: UUID | None,
        reason: str | None,
        history_id: UUID | None = None,
    ) -> None:
        """
        承辦核准案件（UC 對應審查核准後之 application 狀態）。

        責任：僅允許自「已送件／審查中／補件後再送／待補件」轉為 **approved**；已核准／駁回者不可重複。
        """
        terminal = {
            ApplicationStatusPhase.APPROVED.value,
            ApplicationStatusPhase.REJECTED.value,
        }
        if self.status.value in terminal:
            raise InvalidApplicationStateError(
                "Application is already in a terminal review state",
                current_status=self.status.value,
            )
        allowed_from = {
            ApplicationStatusPhase.SUBMITTED.value,
            ApplicationStatusPhase.UNDER_REVIEW.value,
            ApplicationStatusPhase.RESUBMITTED.value,
            ApplicationStatusPhase.SUPPLEMENT_REQUIRED.value,
        }
        if self.status.value not in allowed_from:
            raise InvalidApplicationStateError(
                "Cannot approve application from the current status",
                current_status=self.status.value,
            )
        self.apply_status_transition(
            to_status=ApplicationStatus.approved(),
            now=now,
            changed_by=changed_by,
            reason=reason or "Application approved",
            history_id=history_id,
        )
        self._bump_version_and_touch(now)

    def reject_by_officer(
        self,
        *,
        now: datetime,
        changed_by: UUID | None,
        reason: str | None,
        history_id: UUID | None = None,
    ) -> None:
        """
        承辦駁回案件。

        責任：與 `approve_by_officer` 相同之前置狀態集合，轉為 **rejected**。
        """
        terminal = {
            ApplicationStatusPhase.APPROVED.value,
            ApplicationStatusPhase.REJECTED.value,
        }
        if self.status.value in terminal:
            raise InvalidApplicationStateError(
                "Application is already in a terminal review state",
                current_status=self.status.value,
            )
        allowed_from = {
            ApplicationStatusPhase.SUBMITTED.value,
            ApplicationStatusPhase.UNDER_REVIEW.value,
            ApplicationStatusPhase.RESUBMITTED.value,
            ApplicationStatusPhase.SUPPLEMENT_REQUIRED.value,
        }
        if self.status.value not in allowed_from:
            raise InvalidApplicationStateError(
                "Cannot reject application from the current status",
                current_status=self.status.value,
            )
        self.apply_status_transition(
            to_status=ApplicationStatus.rejected(),
            now=now,
            changed_by=changed_by,
            reason=reason or "Application rejected",
            history_id=history_id,
        )
        self._bump_version_and_touch(now)

    # ------------------------------------------------------------------
    # 狀態歷史（補件需保留歷史：只追加、不修改既有列）
    # ------------------------------------------------------------------

    def apply_status_transition(
        self,
        *,
        to_status: ApplicationStatus,
        now: datetime,
        changed_by: UUID | None,
        reason: str | None,
        history_id: UUID | None = None,
    ) -> None:
        """
        記錄狀態變更並更新當前 status。

        責任：每次轉移新增一筆 StatusHistoryEntry；舊紀錄不可變。
        """
        hid = history_id or uuid4()
        entry = StatusHistoryEntry(
            history_id=hid,
            application_id=self.application_id,
            from_status=self.status.value,
            to_status=to_status.value,
            changed_by=changed_by,
            reason=reason,
            created_at=now,
        )
        self.status_histories.append(entry)
        self.status = to_status

    def _bump_version_and_touch(self, now: datetime) -> None:
        """樂觀並發版本號 + 更新時間。"""
        self.version = int(self.version) + 1
        self.updated_at = now
