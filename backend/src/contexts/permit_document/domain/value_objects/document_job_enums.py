"""
DocumentGenerationJob 之 job_type / status 值物件。

責任：對齊 `permit.document_jobs` 之 varchar 欄位，集中合法集合並供 DocumentGenerationJob 實體使用。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.contexts.permit_document.domain.errors import InvalidPermitValueError


class DocumentJobTypePhase(StrEnum):
    """
    產檔工作類型。

    責任：對應 UC-PERMIT-02 之「套模板、產生各 PDF」等可細分之 job_type；此處先以 **BUNDLE** 表達
    整批產製協調（Infra worker 可再拆子任務而不必全部反映在 domain）。
    """

    GENERATE_PERMIT_BUNDLE = "generate_permit_bundle"


class DocumentJobStatusPhase(StrEnum):
    """
    產檔工作狀態。

    責任：**FAILED** 時寫入 error_message；**不** 於此類別內回滾 Permit 核准狀態，
    改由 Permit 聚合之 `mark_document_regeneration_required` 表達待補產。
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DocumentJobType:
    """
    產檔工作之 **job_type** 值物件（對應 permit.document_jobs.job_type）。

    責任：將持久化字串限制在 **DocumentJobTypePhase** 內；新建工作單時由 App／工廠組裝後傳入 **DocumentGenerationJob**。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in DocumentJobTypePhase}
        if self.value not in allowed:
            raise InvalidPermitValueError(
                f"Invalid document job type: {self.value!r}; expected one of {sorted(allowed)}"
            )


@dataclass(frozen=True)
class DocumentJobStatus:
    """
    產檔工作之 **status** 值物件（對應 permit.document_jobs.status）。

    責任：與 **DocumentGenerationJob** 之狀態機（PENDING→PROCESSING→COMPLETED／FAILED）一致；
    與 **PermitStatus**（許可聚合狀態）分離，避免混淆兩張表之 varchar 語意。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in DocumentJobStatusPhase}
        if self.value not in allowed:
            raise InvalidPermitValueError(
                f"Invalid document job status: {self.value!r}; expected one of {sorted(allowed)}"
            )
