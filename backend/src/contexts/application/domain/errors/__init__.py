"""
Application context — 領域錯誤匯出。

責任：集中匯入 `application_errors` 之例外類型，供 `domain` 套件與 App 層辨識業務違例；
各類別之用途與責任見 `application_errors.py` 內類別 docstring。
"""

from .application_errors import (
    ApplicationDomainError,
    ConsentRequiredError,
    CoreDataNotEditableError,
    InvalidApplicationStateError,
    InvalidDomainValueError,
    RouteRequestMissingError,
    SubmissionRequirementsNotMetError,
    VehicleLimitExceededError,
)

__all__ = [
    "ApplicationDomainError",
    "InvalidDomainValueError",
    "InvalidApplicationStateError",
    "CoreDataNotEditableError",
    "SubmissionRequirementsNotMetError",
    "VehicleLimitExceededError",
    "ConsentRequiredError",
    "RouteRequestMissingError",
]
