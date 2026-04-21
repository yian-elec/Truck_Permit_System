"""
external_identity.py — 外部身分參照值物件

規格 Aggregate 欄位「external_identity_ref」對應資料表之
external_provider + external_subject；封裝為單一值物件以利登入與不變條件表達。
"""

from dataclasses import dataclass

from ..errors import InvalidCredentialInvariantError


@dataclass(frozen=True)
class ExternalIdentityRef:
    """
    外部身分提供者與主體識別（對應 iam.users.external_provider / external_subject）。

    責任：
    - 保證兩欄同時有意義（皆非空白），避免只存其一造成無法比對 IdP 主體。
    """

    provider: str
    subject: str

    def __post_init__(self) -> None:
        pv = (self.provider or "").strip()
        sj = (self.subject or "").strip()
        if not pv or not sj:
            raise InvalidCredentialInvariantError(
                "external provider and subject must both be non-empty"
            )
        object.__setattr__(self, "provider", pv)
        object.__setattr__(self, "subject", sj)
