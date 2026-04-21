"""
Application context — Value objects（值物件）。

責任：對應規格 5.1 所列之 **ApplicationStatus、PermitPeriod、VehiclePlate、AttachmentType、DeliveryMethod**
及申請主表上之 **applicant_type、reason_type、source_channel** 等欄位之領域封裝；
不可變、透過建構／`__post_init__` 校驗，避免無效字串流入聚合。
"""

from .applicant_type import ApplicantType, ApplicantTypeCode
from .application_status import ApplicationStatus, ApplicationStatusPhase
from .attachment_type import AttachmentType
from .delivery_method import DeliveryMethod, DeliveryMethodCode
from .permit_period import PermitPeriod, ensure_utc_aware
from .reason_type import ReasonType
from .source_channel import SourceChannel, SourceChannelCode
from .vehicle_plate import VehiclePlate

__all__ = [
    "ApplicationStatus",
    "ApplicationStatusPhase",
    "PermitPeriod",
    "ensure_utc_aware",
    "VehiclePlate",
    "AttachmentType",
    "DeliveryMethod",
    "DeliveryMethodCode",
    "ApplicantType",
    "ApplicantTypeCode",
    "ReasonType",
    "SourceChannel",
    "SourceChannelCode",
]
