"""
各種代碼與短文字欄位（Value Objects）。

責任：對應 schema 中 varchar 長度與非空約束，集中驗證，避免 Aggregate 內重複邏輯。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..errors import InvalidDomainValueError


def _non_empty_str(label: str, value: str, max_len: int) -> str:
    s = value.strip() if isinstance(value, str) else ""
    if not s:
        raise InvalidDomainValueError(f"{label} must be non-empty")
    if len(s) > max_len:
        raise InvalidDomainValueError(f"{label} exceeds max length {max_len}")
    return s


@dataclass(frozen=True)
class OcrProviderCode:
    """OCR 供應商代碼，對應 ops.ocr_jobs.provider_code varchar(50) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("OcrProviderCode", self.value, 50))


@dataclass(frozen=True)
class OcrFieldName:
    """辨識結果欄位名稱（車號、日期、公司名等），對應 ops.ocr_results.field_name varchar(100) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("OcrFieldName", self.value, 100))


@dataclass(frozen=True)
class NotificationChannel:
    """通知通道（email、sms、push 等），對應 ops.notification_jobs.channel varchar(30) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("NotificationChannel", self.value, 30))


@dataclass(frozen=True)
class TemplateCode:
    """通知模板代碼，對應 ops.notification_jobs.template_code varchar(50) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("TemplateCode", self.value, 50))


@dataclass(frozen=True)
class ActorType:
    """
    稽核行為主體類型（user、system、integration 等）。

    對應 ops.audit_logs.actor_type varchar(30) not null；actor_user_id 可為空表示非人類主體。
    """

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("ActorType", self.value, 30))


@dataclass(frozen=True)
class ActionCode:
    """稽核動作代碼，對應 ops.audit_logs.action_code varchar(100) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("ActionCode", self.value, 100))


@dataclass(frozen=True)
class ResourceType:
    """被操作資源類型，對應 ops.audit_logs.resource_type varchar(50) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("ResourceType", self.value, 50))


@dataclass(frozen=True)
class ResourceId:
    """被操作資源識別，對應 ops.audit_logs.resource_id varchar(100) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("ResourceId", self.value, 100))


@dataclass(frozen=True)
class ImportJobType:
    """匯入作業類型（例如 holiday、routing_rules、map 等），對應 ops.import_jobs.job_type varchar(50) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("ImportJobType", self.value, 50))


@dataclass(frozen=True)
class ImportSourceName:
    """資料來源名稱，對應 ops.import_jobs.source_name varchar(100) not null。"""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _non_empty_str("ImportSourceName", self.value, 100))


@dataclass(frozen=True)
class ImportSourceRef:
    """選填的來源參照（URL、檔名、批次 id），對應 ops.import_jobs.source_ref varchar(255) null。"""

    value: str | None

    def __post_init__(self) -> None:
        if self.value is None:
            return
        s = self.value.strip()
        if len(s) > 255:
            raise InvalidDomainValueError("ImportSourceRef exceeds max length 255")
        object.__setattr__(self, "value", s or None)


@dataclass(frozen=True)
class NotificationPayload:
    """
    通知模板變數 payload，對應 ops.notification_jobs.payload_json jsonb not null。

    責任：確保為非空 mapping，實際 JSON 序列化由 Infra 層處理；領域僅持有結構化資料。
    """

    data: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.data, Mapping):
            raise InvalidDomainValueError("NotificationPayload must be a mapping")
        if len(self.data) == 0:
            raise InvalidDomainValueError("NotificationPayload must be non-empty")
