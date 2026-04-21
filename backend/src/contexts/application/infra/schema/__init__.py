"""
Application context — infra schema（application.* 與 ops.stored_files）。

init_db 掃描並匯入本目錄內之 *.py（不含 __init__），再執行 Base.metadata.create_all。
"""

from .applicant_profiles import ApplicantProfiles
from .applications import Applications
from .attachments import Attachments
from .checklists import Checklists
from .company_profiles import CompanyProfiles
from .status_histories import StatusHistories
from .stored_files import StoredFiles
from .vehicles import Vehicles

__all__ = [
    "Applications",
    "ApplicantProfiles",
    "CompanyProfiles",
    "Vehicles",
    "Attachments",
    "StatusHistories",
    "Checklists",
    "StoredFiles",
]
