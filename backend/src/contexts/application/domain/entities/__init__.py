"""
Application context — 實體與聚合根。

責任：對應規格 5.1——**Application** 為 Aggregate Root；**ApplicantProfile**、**CompanyProfile**、**Vehicle**、
**ChecklistItem**、**StatusHistoryEntry** 等為聚合內實體；**AttachmentBundle**（含 **AttachmentDescriptor**）
表達必備項目／已上傳項目／檢核狀態；**SubmissionReadiness** 為送件前檢查之領域結果值（非 ORM 實體）。
"""

from .applicant_profile import ApplicantProfile
from .application import Application, MAX_VEHICLES_PER_APPLICATION
from .attachment_bundle import AttachmentBundle
from .attachment_descriptor import AttachmentDescriptor
from .checklist_item import ChecklistItem
from .company_profile import CompanyProfile
from .status_history_entry import StatusHistoryEntry
from .submission_readiness import SubmissionReadiness
from .vehicle import Vehicle

__all__ = [
    "Application",
    "MAX_VEHICLES_PER_APPLICATION",
    "ApplicantProfile",
    "CompanyProfile",
    "Vehicle",
    "AttachmentBundle",
    "AttachmentDescriptor",
    "ChecklistItem",
    "StatusHistoryEntry",
    "SubmissionReadiness",
]
