"""
Application 埠（Protocol）。

與「用例編排」類別分離：此目錄僅定義邊界介面，不含流程邏輯；
實作由 Infra 或其他 context 注入。
"""

from .external_ports import (
    AttachmentBlobPort,
    AttachmentOcrStatusPort,
    ImportIngestionPort,
    NotificationDispatchPort,
    OcrExtractorPort,
)
from .ops_read_port import OpsReadPort

__all__ = [
    "OpsReadPort",
    "AttachmentBlobPort",
    "OcrExtractorPort",
    "AttachmentOcrStatusPort",
    "NotificationDispatchPort",
    "ImportIngestionPort",
]
