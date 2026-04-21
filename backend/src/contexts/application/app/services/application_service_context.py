"""
用例服務共用執行上下文（載入聚合、擁有者檢查、PATCH、儲存、領域錯誤轉換）。

責任：集中「與單一用例無關、多個 Application*Service 重複使用」之流程；
各專責服務僅注入本上下文，不直接持有零散的 repository／read_model 參考，以降低重複與耦合。
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from src.contexts.application.domain.entities import Application
from src.contexts.application.domain.errors import ApplicationDomainError
from src.contexts.application.domain.repositories import ApplicationReadModelQuery
from src.contexts.application.domain.value_objects import (
    DeliveryMethod,
    PermitPeriod,
    ReasonType,
    ensure_utc_aware,
)
from src.contexts.application.infra.repositories import ApplicationRepositoryImpl

from ..dtos import PatchApplicationInputDTO, PatchApplicationProfilesInputDTO
from ..errors import (
    ApplicationNotFoundAppError,
    ApplicationValidationAppError,
    to_app_error,
)
from .application_mappers import applicant_dto_to_entity, company_dto_to_entity
from .ports.outbound import (
    ApplicationEventPublisher,
    FileStoragePort,
    SupplementWorkflowPort,
)

T = TypeVar("T")


def raise_domain_as_app(fn: Callable[[], T]) -> T:
    """執行可拋出領域例外的呼叫，並轉為 App 層錯誤。"""
    try:
        return fn()
    except ApplicationDomainError as e:
        raise to_app_error(e) from e


class ApplicationServiceContext:
    """
    申請案件用例之共享依賴與輔助方法。

    責任：單一實例由外觀 `ApplicationCommandService` 建立後注入各 `*ApplicationService`；
    不承擔具體 UC 業務敘述，只做技術性前置／後置。
    """

    def __init__(
        self,
        *,
        repository: ApplicationRepositoryImpl,
        read_model: ApplicationReadModelQuery,
        file_storage: FileStoragePort,
        event_publisher: ApplicationEventPublisher,
        supplement_workflow: SupplementWorkflowPort,
        max_permit_calendar_days: int,
    ) -> None:
        self.repo = repository
        self.read = read_model
        self.files = file_storage
        self.events = event_publisher
        self.supplement = supplement_workflow
        self.max_permit_calendar_days = max_permit_calendar_days

    def load(self, application_id: UUID) -> Application:
        """依主鍵載入聚合；不存在時拋 404 語意之 App 錯誤。"""
        app = self.repo.get_by_id(application_id)
        if app is None:
            raise ApplicationNotFoundAppError(
                "申請案件不存在",
                details={"application_id": str(application_id)},
            )
        return app

    def ensure_applicant(
        self,
        app: Application,
        applicant_user_id: UUID | None,
    ) -> None:
        """若帶入登入使用者，必須與案件 applicant_user_id 一致（避免水平越權）。"""
        if applicant_user_id is None:
            return
        if app.applicant_user_id != applicant_user_id:
            raise ApplicationNotFoundAppError(
                "申請案件不存在",
                details={"application_id": str(app.application_id)},
            )

    def save(self, app: Application) -> None:
        try:
            self.repo.save(app)
        except Exception as e:
            raise to_app_error(e) from e

    def apply_patch_core(
        self,
        app: Application,
        patch: PatchApplicationInputDTO,
        now: datetime,
    ) -> None:
        """更新主表核心欄位（事由、期間、送達方式）。"""
        period: PermitPeriod | None = None
        if patch.requested_start_at is not None and patch.requested_end_at is not None:
            period = PermitPeriod(
                start_at=ensure_utc_aware(patch.requested_start_at),
                end_at=ensure_utc_aware(patch.requested_end_at),
            )
        elif patch.requested_start_at is not None or patch.requested_end_at is not None:
            raise ApplicationValidationAppError(
                "requested_start_at 與 requested_end_at 需同時提供",
                details={},
            )

        raise_domain_as_app(
            lambda: app.update_application_core(
                reason_type=ReasonType(patch.reason_type) if patch.reason_type else None,
                reason_detail=patch.reason_detail,
                requested_period=period,
                delivery_method=DeliveryMethod(patch.delivery_method)
                if patch.delivery_method
                else None,
                now=now,
            )
        )

    def apply_profiles(
        self,
        app: Application,
        profiles: PatchApplicationProfilesInputDTO,
        now: datetime,
    ) -> None:
        """整體取代申請人／公司區塊。"""
        if profiles.applicant is not None:
            ent = applicant_dto_to_entity(
                profiles.applicant,
                application_id=app.application_id,
                now=now,
            )
            raise_domain_as_app(lambda: app.replace_applicant_profile(ent, now=now))
        if profiles.company is not None:
            ent = company_dto_to_entity(
                profiles.company,
                application_id=app.application_id,
                now=now,
            )
            raise_domain_as_app(lambda: app.replace_company_profile(ent, now=now))
