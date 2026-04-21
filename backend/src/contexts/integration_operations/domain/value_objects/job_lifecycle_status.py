"""
作業生命週期狀態（Value Object）。

責任：描述 OCR Job、Import Job 等長流程作業在領域中的合法狀態，
並集中校驗狀態字串，與資料表 ops.*_jobs.status 對齊（varchar(30)）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import InvalidDomainValueError


class JobLifecyclePhase(StrEnum):
    """
    長流程作業的標準階段。

    責任：與 UC-OPS-01、UC-OPS-04 中「建立 job → 執行 → 成功／失敗」的語意一致。
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class JobLifecycleStatus:
    """
    封裝於 DB 中持久化的 status 字串，並限制為已知階段之一。

    用途：由 Aggregate 在狀態轉移時持有，避免任意字串污染領域模型。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in JobLifecyclePhase}
        if self.value not in allowed:
            raise InvalidDomainValueError(
                f"Invalid job lifecycle status: {self.value!r}; expected one of {sorted(allowed)}"
            )

    @classmethod
    def pending(cls) -> JobLifecycleStatus:
        """建立尚未開始執行的作業狀態。"""
        return cls(JobLifecyclePhase.PENDING.value)

    @classmethod
    def running(cls) -> JobLifecycleStatus:
        """作業已開始（例如已從 storage 取檔、或已開始匯入）。"""
        return cls(JobLifecyclePhase.RUNNING.value)

    @classmethod
    def succeeded(cls) -> JobLifecycleStatus:
        """作業成功完成。"""
        return cls(JobLifecyclePhase.SUCCEEDED.value)

    @classmethod
    def failed(cls) -> JobLifecycleStatus:
        """作業失敗並應附錯誤訊息（由 Aggregate 另行持有）。"""
        return cls(JobLifecyclePhase.FAILED.value)

    def is_terminal(self) -> bool:
        """是否已結束（成功或失敗），之後不可再轉為 running。"""
        return self.value in (
            JobLifecyclePhase.SUCCEEDED.value,
            JobLifecyclePhase.FAILED.value,
        )
