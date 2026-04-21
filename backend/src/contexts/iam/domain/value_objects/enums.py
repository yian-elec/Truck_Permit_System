"""
enums.py — IAM 列舉型值物件

對應規格中的帳戶類型、狀態與 MFA 方式；以 Enum 表達有限集合與業務語意。
"""

from enum import Enum


class AccountType(str, Enum):
    """
    帳戶類型：民眾（申請人）、承辦、管理者、系統帳號。
    民眾與承辦共用同一 User 模型，僅以此欄位區分行為與規則。
    """

    APPLICANT = "applicant"
    OFFICER = "officer"
    ADMIN = "admin"
    SYSTEM = "system"


class AccountStatus(str, Enum):
    """帳戶生命週期狀態，影響是否可登入與是否需額外審核。"""

    ACTIVE = "active"
    DISABLED = "disabled"
    LOCKED = "locked"
    PENDING = "pending"


class MfaMethod(str, Enum):
    """
    MFA 驗證管道種類（對應 iam.mfa_challenges.method）。
    實際發送簡訊／Email 由 App + Infra 的 MfaSenderPort 處理，領域僅保存類型。
    """

    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"
