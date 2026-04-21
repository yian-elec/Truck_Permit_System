"""
Permit_Document — infra schema（permit.*）。

init_db 掃描本目錄 `*.py`（不含 __init__）並匯入模組，使 ORM 註冊至 Base.metadata。
"""

from .certificate_access_logs import CertificateAccessLogs
from .document_jobs import DocumentJobs
from .documents import Documents
from .permits import Permits

__all__ = [
    "Permits",
    "Documents",
    "DocumentJobs",
    "CertificateAccessLogs",
]
