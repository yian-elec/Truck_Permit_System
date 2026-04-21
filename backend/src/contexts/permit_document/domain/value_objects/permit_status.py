"""
PermitStatus、PermitAggregateStatus — 許可證聚合與文件列之狀態值物件。

責任：與 persistence 之 `status varchar(30)` 對齊，集中合法狀態集合，
避免任意字串污染聚合；「核准不因文件失敗回滾」以 **ISSUED_WITH_PENDING_DOCUMENT_REGEN** 等語意表達。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.contexts.permit_document.domain.errors import InvalidPermitValueError


class PermitAggregateStatusPhase(StrEnum):
    """
    Permit 聚合根在生命週期中的標準階段（對應 permit.permits.status）。

    責任：對齊 §8（pending_generation／issued／generation_failed／revoked／expired）並保留
    **issued_pending_document_regen** 表達「已核發但待補產」。
    """

    PENDING_GENERATION = "pending_generation"
    ISSUED = "issued"
    GENERATION_FAILED = "generation_failed"
    REVOKED = "revoked"
    EXPIRED = "expired"
    ISSUED_WITH_PENDING_DOCUMENT_REGEN = "issued_pending_document_regen"


@dataclass(frozen=True)
class PermitAggregateStatus:
    """
    封裝 permit 聚合狀態字串，並限制為已知階段之一。

    責任：由 Permit 聚合持有；狀態轉移由聚合方法執行並替換實例或更新內部欄位（此處為 VO，替換為主）。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in PermitAggregateStatusPhase}
        if self.value not in allowed:
            raise InvalidPermitValueError(
                f"Invalid permit aggregate status: {self.value!r}; expected one of {sorted(allowed)}"
            )

    @classmethod
    def pending_generation(cls) -> PermitAggregateStatus:
        """等待使用證 PDF 產製（§8 pending_generation）。"""
        return cls(PermitAggregateStatusPhase.PENDING_GENERATION.value)

    @classmethod
    def issued(cls) -> PermitAggregateStatus:
        """已核發且文件流程正常完成（或已補齊）。"""
        return cls(PermitAggregateStatusPhase.ISSUED.value)

    @classmethod
    def issued_with_pending_document_regen(cls) -> PermitAggregateStatus:
        """已核發，但需待補產文件（不回滾核准）。"""
        return cls(PermitAggregateStatusPhase.ISSUED_WITH_PENDING_DOCUMENT_REGEN.value)


class PermitDocumentRecordStatusPhase(StrEnum):
    """
    單一文件列（permit.documents）之狀態。

    責任：
    - **PENDING**：已建列／等待寫入 storage 與 file_id。
    - **ACTIVE**：目前有效版本，可供下載語意使用。
    - **FAILED**：產製失敗；不影響 permit 核准，由聚合標示待補產。
    - **SUPERSEDED**：被新版本取代；**文件重產需保留版本** 時舊列進入此狀態。
    """

    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class PermitDocumentRecordStatus:
    """
    單一文件列（permit.documents）之 **status** 值物件。

    責任：與持久化 varchar(30) 對齊之封閉集合；**非**規格 8.1 圖中的「Permit 之 PermitStatus」
    （後者見 **PermitStatus**／PermitAggregateStatus）。轉移由 **PermitDocument** 實體方法執行。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in PermitDocumentRecordStatusPhase}
        if self.value not in allowed:
            raise InvalidPermitValueError(
                f"Invalid document record status: {self.value!r}; expected one of {sorted(allowed)}"
            )

    @classmethod
    def pending(cls) -> PermitDocumentRecordStatus:
        return cls(PermitDocumentRecordStatusPhase.PENDING.value)

    @classmethod
    def active(cls) -> PermitDocumentRecordStatus:
        return cls(PermitDocumentRecordStatusPhase.ACTIVE.value)

    @classmethod
    def failed(cls) -> PermitDocumentRecordStatus:
        return cls(PermitDocumentRecordStatusPhase.FAILED.value)

    @classmethod
    def superseded(cls) -> PermitDocumentRecordStatus:
        return cls(PermitDocumentRecordStatusPhase.SUPERSEDED.value)


# ---------------------------------------------------------------------------
# 規格 8.1 所稱 **PermitStatus**：與 **PermitAggregateStatus** 為同一值物件型別（別名）。
# 實作名稱保留 Aggregate 前綴以區分「許可聚合狀態」與「文件列狀態」兩種 varchar 語意。
# ---------------------------------------------------------------------------
PermitStatus = PermitAggregateStatus
PermitStatusPhase = PermitAggregateStatusPhase
