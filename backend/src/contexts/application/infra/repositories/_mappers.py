"""
Application 聚合 ↔ ORM 映射（Infra 內部）。

責任：純資料轉換；不開啟 session。附件列由 DB 完整載入並轉成領域 AttachmentDescriptor；
聚合內 Descriptor 不含 file_id，故 save 僅同步 checklists／主表／profiles／vehicles／histories，
attachments 表由 UC-APP-04 等流程另行寫入。
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable
from uuid import UUID

from src.contexts.application.domain.entities import (
    ApplicantProfile,
    Application,
    AttachmentBundle,
    AttachmentDescriptor,
    ChecklistItem,
    CompanyProfile,
    StatusHistoryEntry,
    Vehicle,
)
from src.contexts.application.domain.value_objects import (
    ApplicantType,
    ApplicationStatus,
    AttachmentType,
    DeliveryMethod,
    PermitPeriod,
    ReasonType,
    SourceChannel,
    VehiclePlate,
)
from src.contexts.application.infra.schema import (
    ApplicantProfiles,
    Applications,
    Attachments,
    Checklists,
    CompanyProfiles,
    StatusHistories,
    Vehicles,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def attachment_row_to_descriptor(row: Attachments) -> AttachmentDescriptor:
    return AttachmentDescriptor(
        attachment_id=row.attachment_id,
        attachment_type=AttachmentType(row.attachment_type),
        status=row.status,
        ocr_status=row.ocr_status,
    )


def checklist_row_to_item(row: Checklists) -> ChecklistItem:
    return ChecklistItem(
        checklist_id=row.checklist_id,
        item_code=row.item_code,
        item_name=row.item_name,
        is_required=row.is_required,
        is_satisfied=row.is_satisfied,
        source=row.source,
        note=row.note,
    )


def rows_to_aggregate(
    app_row: Applications,
    applicant_row: ApplicantProfiles | None,
    company_row: CompanyProfiles | None,
    vehicle_rows: Iterable[Vehicles],
    checklist_rows: Iterable[Checklists],
    attachment_rows: Iterable[Attachments],
    history_rows: Iterable[StatusHistories],
) -> Application:
    """由 ORM 列組裝領域聚合（假設 app_row 非空）。"""
    vehicles_sorted = sorted(vehicle_rows, key=lambda v: v.created_at)
    histories_sorted = sorted(history_rows, key=lambda h: h.created_at)
    checklists_sorted = sorted(checklist_rows, key=lambda c: c.created_at)

    applicant = None
    if applicant_row:
        applicant = ApplicantProfile(
            application_id=applicant_row.application_id,
            name=applicant_row.name,
            id_no=applicant_row.id_no,
            gender=applicant_row.gender,
            email=applicant_row.email,
            mobile=applicant_row.mobile,
            phone_area=applicant_row.phone_area,
            phone_no=applicant_row.phone_no,
            phone_ext=applicant_row.phone_ext,
            address_county=applicant_row.address_county,
            address_district=applicant_row.address_district,
            address_detail=applicant_row.address_detail,
            created_at=applicant_row.created_at,
            updated_at=applicant_row.updated_at,
        )

    company = None
    if company_row:
        company = CompanyProfile(
            application_id=company_row.application_id,
            company_name=company_row.company_name,
            tax_id=company_row.tax_id,
            principal_name=company_row.principal_name,
            contact_name=company_row.contact_name,
            contact_mobile=company_row.contact_mobile,
            contact_phone=company_row.contact_phone,
            address=company_row.address,
            created_at=company_row.created_at,
            updated_at=company_row.updated_at,
        )

    dom_vehicles: list[Vehicle] = []
    for vr in vehicles_sorted:
        trailer_raw = (vr.trailer_plate_no or "").strip()
        trailer = VehiclePlate(trailer_raw) if trailer_raw else None
        dom_vehicles.append(
            Vehicle(
                vehicle_id=vr.vehicle_id,
                application_id=vr.application_id,
                plate_no=VehiclePlate(vr.plate_no),
                vehicle_kind=vr.vehicle_kind,
                gross_weight_ton=Decimal(vr.gross_weight_ton) if vr.gross_weight_ton is not None else None,
                license_valid_until=vr.license_valid_until,
                trailer_plate_no=trailer,
                is_primary=vr.is_primary,
                created_at=vr.created_at,
                updated_at=vr.updated_at,
            )
        )

    checklist_items = [checklist_row_to_item(r) for r in checklists_sorted]
    uploaded = [attachment_row_to_descriptor(r) for r in attachment_rows]
    bundle = AttachmentBundle(checklist_items=checklist_items, uploaded=uploaded)

    histories = [
        StatusHistoryEntry(
            history_id=h.history_id,
            application_id=h.application_id,
            from_status=h.from_status,
            to_status=h.to_status,
            changed_by=h.changed_by,
            reason=h.reason,
            created_at=h.created_at,
        )
        for h in histories_sorted
    ]

    period = PermitPeriod(
        start_at=app_row.requested_start_at,
        end_at=app_row.requested_end_at,
    )

    return Application(
        application_id=app_row.application_id,
        application_no=app_row.application_no,
        status=ApplicationStatus(app_row.status),
        applicant_type=ApplicantType(app_row.applicant_type),
        reason_type=ReasonType(app_row.reason_type),
        reason_detail=app_row.reason_detail,
        requested_period=period,
        delivery_method=DeliveryMethod(app_row.delivery_method),
        source_channel=SourceChannel(app_row.source_channel),
        applicant_user_id=app_row.applicant_user_id,
        consent_accepted_at=app_row.consent_accepted_at,
        submitted_at=app_row.submitted_at,
        version=int(app_row.version),
        created_at=app_row.created_at,
        updated_at=app_row.updated_at,
        applicant_profile=applicant,
        company_profile=company,
        vehicles=dom_vehicles,
        attachment_bundle=bundle,
        status_histories=histories,
    )


def applications_row_from_aggregate(app: Application, *, updated_at: datetime | None = None) -> Applications:
    """建立／更新用之主表 ORM 物件（不加入 session）。"""
    ts = updated_at or _utc_now()
    return Applications(
        application_id=app.application_id,
        application_no=app.application_no,
        applicant_user_id=app.applicant_user_id,
        status=app.status.value,
        applicant_type=app.applicant_type.value,
        reason_type=app.reason_type.value,
        reason_detail=app.reason_detail,
        requested_start_at=app.requested_period.start_at,
        requested_end_at=app.requested_period.end_at,
        delivery_method=app.delivery_method.value,
        source_channel=app.source_channel.value,
        consent_accepted_at=app.consent_accepted_at,
        submitted_at=app.submitted_at,
        version=app.version,
        created_at=app.created_at,
        updated_at=ts,
    )


def applicant_row_from_profile(p: ApplicantProfile, *, updated_at: datetime | None = None) -> ApplicantProfiles:
    ts = updated_at or _utc_now()
    return ApplicantProfiles(
        application_id=p.application_id,
        name=p.name,
        id_no=p.id_no,
        gender=p.gender,
        email=p.email,
        mobile=p.mobile,
        phone_area=p.phone_area,
        phone_no=p.phone_no,
        phone_ext=p.phone_ext,
        address_county=p.address_county,
        address_district=p.address_district,
        address_detail=p.address_detail,
        created_at=p.created_at,
        updated_at=ts,
    )


def company_row_from_profile(p: CompanyProfile, *, updated_at: datetime | None = None) -> CompanyProfiles:
    ts = updated_at or _utc_now()
    return CompanyProfiles(
        application_id=p.application_id,
        company_name=p.company_name,
        tax_id=p.tax_id,
        principal_name=p.principal_name,
        contact_name=p.contact_name,
        contact_mobile=p.contact_mobile,
        contact_phone=p.contact_phone,
        address=p.address,
        created_at=p.created_at,
        updated_at=ts,
    )


def vehicle_row_from_entity(v: Vehicle, *, updated_at: datetime | None = None) -> Vehicles:
    ts = updated_at or _utc_now()
    return Vehicles(
        vehicle_id=v.vehicle_id,
        application_id=v.application_id,
        plate_no=v.plate_no.value,
        vehicle_kind=v.vehicle_kind,
        gross_weight_ton=v.gross_weight_ton,
        license_valid_until=v.license_valid_until,
        trailer_plate_no=v.trailer_plate_no.value if v.trailer_plate_no else None,
        is_primary=v.is_primary,
        created_at=v.created_at,
        updated_at=ts,
    )


def checklist_row_from_item(application_id: UUID, item: ChecklistItem, *, now: datetime | None = None) -> Checklists:
    ts = now or _utc_now()
    return Checklists(
        checklist_id=item.checklist_id,
        application_id=application_id,
        item_code=item.item_code,
        item_name=item.item_name,
        is_required=item.is_required,
        is_satisfied=item.is_satisfied,
        source=item.source,
        note=item.note,
        created_at=ts,
        updated_at=ts,
    )


def history_row_from_entry(h: StatusHistoryEntry) -> StatusHistories:
    return StatusHistories(
        history_id=h.history_id,
        application_id=h.application_id,
        from_status=h.from_status,
        to_status=h.to_status,
        changed_by=h.changed_by,
        reason=h.reason,
        created_at=h.created_at,
    )
