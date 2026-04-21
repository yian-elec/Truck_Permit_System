"""
領域聚合／讀模型 → App DTO 映射。

責任：集中轉換邏輯，避免服務方法內散落欄位拷貝。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.contexts.application.domain.entities import ApplicantProfile, Application, CompanyProfile, Vehicle
from src.contexts.application.domain.read_models import AttachmentSummaryView

from ..dtos import (
    ApplicantProfileDTO,
    ApplicationDetailDTO,
    ApplicationSummaryDTO,
    AttachmentSummaryDTO,
    ChecklistItemDTO,
    CompanyProfileDTO,
    StatusHistoryEntryDTO,
    VehicleDTO,
)


def attachment_view_to_dto(view: AttachmentSummaryView) -> AttachmentSummaryDTO:
    """讀模型附件視圖 → API DTO。"""
    return AttachmentSummaryDTO(
        attachment_id=view.attachment_id,
        attachment_type=view.attachment_type,
        file_id=view.file_id,
        original_filename=view.original_filename,
        mime_type=view.mime_type,
        size_bytes=view.size_bytes,
        status=view.status,
        ocr_status=view.ocr_status,
        uploaded_by=view.uploaded_by,
        uploaded_at=view.uploaded_at,
    )


def applicant_entity_to_dto(p: ApplicantProfile) -> ApplicantProfileDTO:
    return ApplicantProfileDTO(
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
    )


def company_entity_to_dto(p: CompanyProfile) -> CompanyProfileDTO:
    return CompanyProfileDTO(
        company_name=p.company_name,
        tax_id=p.tax_id,
        principal_name=p.principal_name,
        contact_name=p.contact_name,
        contact_mobile=p.contact_mobile,
        contact_phone=p.contact_phone,
        address=p.address,
    )


def vehicle_entity_to_dto(v: Vehicle) -> VehicleDTO:
    return VehicleDTO(
        vehicle_id=v.vehicle_id,
        application_id=v.application_id,
        plate_no=v.plate_no.value,
        vehicle_kind=v.vehicle_kind,
        gross_weight_ton=v.gross_weight_ton,
        license_valid_until=v.license_valid_until,
        trailer_plate_no=v.trailer_plate_no.value if v.trailer_plate_no else None,
        is_primary=v.is_primary,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )


def checklist_entity_to_dto(app: Application) -> list[ChecklistItemDTO]:
    return [
        ChecklistItemDTO(
            checklist_id=item.checklist_id,
            item_code=item.item_code,
            item_name=item.item_name,
            is_required=item.is_required,
            is_satisfied=item.is_satisfied,
            source=item.source,
            note=item.note,
        )
        for item in app.attachment_bundle.checklist_items
    ]


def status_history_to_dtos(app: Application) -> list[StatusHistoryEntryDTO]:
    return [
        StatusHistoryEntryDTO(
            history_id=h.history_id,
            from_status=h.from_status,
            to_status=h.to_status,
            changed_by=h.changed_by,
            reason=h.reason,
            created_at=h.created_at,
        )
        for h in app.status_histories
    ]


def application_to_summary_dto(app: Application) -> ApplicationSummaryDTO:
    return ApplicationSummaryDTO(
        application_id=app.application_id,
        application_no=app.application_no,
        status=app.status.value,
        applicant_type=app.applicant_type.value,
        updated_at=app.updated_at,
    )


def application_to_detail_dto(
    app: Application,
    *,
    attachment_views: list[AttachmentSummaryView],
) -> ApplicationDetailDTO:
    """組裝案件明細；附件列以讀模型為準（含 file_id 等完整欄位）。"""
    return ApplicationDetailDTO(
        application_id=app.application_id,
        application_no=app.application_no,
        status=app.status.value,
        applicant_type=app.applicant_type.value,
        reason_type=app.reason_type.value,
        reason_detail=app.reason_detail,
        requested_start_at=app.requested_period.start_at,
        requested_end_at=app.requested_period.end_at,
        delivery_method=app.delivery_method.value,
        source_channel=app.source_channel.value,
        applicant_user_id=app.applicant_user_id,
        consent_accepted_at=app.consent_accepted_at,
        submitted_at=app.submitted_at,
        version=app.version,
        created_at=app.created_at,
        updated_at=app.updated_at,
        applicant=applicant_entity_to_dto(app.applicant_profile)
        if app.applicant_profile
        else None,
        company=company_entity_to_dto(app.company_profile) if app.company_profile else None,
        vehicles=[vehicle_entity_to_dto(v) for v in app.vehicles],
        checklist=checklist_entity_to_dto(app),
        attachments=[attachment_view_to_dto(v) for v in attachment_views],
        status_history=status_history_to_dtos(app),
    )


def applicant_dto_to_entity(
    dto: ApplicantProfileDTO,
    *,
    application_id: UUID,
    now: datetime,
) -> ApplicantProfile:
    """DTO → 領域實體（新建或整體取代）。"""
    return ApplicantProfile(
        application_id=application_id,
        name=dto.name,
        id_no=dto.id_no,
        gender=dto.gender,
        email=dto.email,
        mobile=dto.mobile,
        phone_area=dto.phone_area,
        phone_no=dto.phone_no,
        phone_ext=dto.phone_ext,
        address_county=dto.address_county,
        address_district=dto.address_district,
        address_detail=dto.address_detail,
        created_at=now,
        updated_at=now,
    )


def company_dto_to_entity(
    dto: CompanyProfileDTO,
    *,
    application_id: UUID,
    now: datetime,
) -> CompanyProfile:
    return CompanyProfile(
        application_id=application_id,
        company_name=dto.company_name,
        tax_id=dto.tax_id,
        principal_name=dto.principal_name,
        contact_name=dto.contact_name,
        contact_mobile=dto.contact_mobile,
        contact_phone=dto.contact_phone,
        address=dto.address,
        created_at=now,
        updated_at=now,
    )
