"""
Review_Decision — API E2E 共用 fixture。

- 經 `TestClient` 使用真實 `main:app`（AuthMiddleware + 審查路由器 + 與正式環境相同之依賴工廠）。
- 模組級重建相關 schema 並 `init_db()`，與 Application E2E 一致，確保 routing.* 存在、審查讀路線不會因缺表而 500。
- 種子資料僅透過 `get_review_api_bundle()` 取得之 Application／Review 服務寫入 DB，**不**發 HTTP 至其他 context 之路由。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from shared.core.db.connection import get_engine
from shared.core.db.init_db import init_db


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Review_Decision API E2E requires PostgreSQL")


@pytest.fixture(scope="module")
def review_decision_e2e_db_ready() -> None:
    """清空主要業務 schema 後重建（含 review、routing），載入 seed。"""
    _require_postgresql()
    eng = get_engine()
    with eng.begin() as conn:
        for schema in ("review", "routing", "application", "ops"):
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
    eng.dispose()
    if not init_db():
        pytest.skip("init_db() failed (check PostgreSQL / PostGIS / logs)")
    yield
    get_engine().dispose()


@pytest.fixture(scope="module")
def e2e_client(review_decision_e2e_db_ready):
    """真實 FastAPI `main:app`。"""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


# 固定承辦 UUID，JWT sub 與分派／寫入決策之使用者一致
OFFICER_USER_ID = UUID("660e8400-e29b-41d4-a716-446655440099")


@pytest.fixture(scope="module")
def officer_auth_headers() -> dict[str, str]:
    from shared.core.security.jwt.jwt_handler import JWTHandler

    token = JWTHandler().encode(str(OFFICER_USER_ID), roles=["officer"])
    return {"Authorization": f"Bearer {token}"}


def seed_submitted_application_with_attachment() -> tuple[UUID, UUID, UUID]:
    """
    建立已送件案件並完成一筆附件（與 App 整合測試相同步驟）。

    Returns:
        (application_id, attachment_id, applicant_user_id)
    """
    from src.contexts.application.app.dtos import (
        AddVehicleInputDTO,
        ApplicantProfileDTO,
        CompleteAttachmentUploadInputDTO,
        CreateDraftApplicationInputDTO,
        PatchApplicationProfilesInputDTO,
        RequestUploadUrlInputDTO,
    )
    from src.contexts.review_decision.api.dependencies import get_review_api_bundle

    applicant_user_id = uuid4()
    bundle = get_review_api_bundle()
    now = datetime.now(timezone.utc)
    draft = bundle.app_cmd.create_draft(
        CreateDraftApplicationInputDTO(
            applicant_type="natural_person",
            reason_type="heavy_truck_permit",
            reason_detail=None,
            requested_start_at=now,
            requested_end_at=now + timedelta(days=30),
            delivery_method="online",
            source_channel="web",
        ),
        applicant_user_id=applicant_user_id,
    )
    aid = draft.application_id
    bundle.app_cmd.update_draft_application(
        aid,
        profiles=PatchApplicationProfilesInputDTO(
            applicant=ApplicantProfileDTO(
                name="E2E 審查測試申請人",
                id_no="E223456789",
                gender="M",
                email="review.e2e@test.local",
                mobile="0911222333",
            )
        ),
        applicant_user_id=applicant_user_id,
    )
    bundle.app_cmd.add_vehicle(
        aid,
        AddVehicleInputDTO(plate_no="E2E-1001", vehicle_kind="heavy_truck"),
        applicant_user_id=applicant_user_id,
    )
    url_out = bundle.app_cmd.create_attachment_upload_url(
        aid,
        RequestUploadUrlInputDTO(mime_type="application/pdf"),
        applicant_user_id=applicant_user_id,
    )
    attachment_id = uuid4()
    bundle.app_cmd.complete_attachment_upload(
        aid,
        CompleteAttachmentUploadInputDTO(
            file_id=url_out.file_id,
            attachment_id=attachment_id,
            attachment_type="id_card",
            original_filename="id.pdf",
            mime_type="application/pdf",
            size_bytes=2048,
            checksum_sha256="e" * 64,
            bucket_name="test-bucket",
            object_key=url_out.object_key,
            storage_provider="s3",
        ),
        applicant_user_id=applicant_user_id,
    )
    bundle.app_cmd.record_consent(aid, applicant_user_id=applicant_user_id)
    bundle.app_cmd.submit_application(
        aid,
        applicant_user_id=applicant_user_id,
        changed_by=applicant_user_id,
    )
    return aid, attachment_id, applicant_user_id


def seed_review_task_for_application(application_id: UUID) -> None:
    from src.contexts.review_decision.api.dependencies import get_review_api_bundle
    from src.contexts.review_decision.app.dtos import CreateReviewTaskInputDTO

    bundle = get_review_api_bundle()
    bundle.r_cmd.create_pending_review_task(
        CreateReviewTaskInputDTO(application_id=application_id),
    )
