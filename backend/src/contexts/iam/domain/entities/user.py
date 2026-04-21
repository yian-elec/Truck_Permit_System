"""
user.py — User 聚合根

對應規格 Aggregate「User」與 iam.users：民眾與承辦共用此模型，以 account_type 區分。
`external_identity_ref` 以值物件 `ExternalIdentityRef` 表達（持久化為 external_provider + external_subject）。
核心規則在類別內強制：承辦／管理者須有角色且強制 MFA；Credential 來源二選一（密碼雜湊或外部身分）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..errors import (
    InvalidCredentialInvariantError,
    InvalidDisplayNameError,
    InvalidUserStateError,
    OfficerAdminRequiresMfaError,
    OfficerAdminRequiresRoleError,
)
from ..value_objects import (
    AccountStatus,
    AccountType,
    AssignmentScope,
    ExternalIdentityRef,
    RoleAssignmentId,
    RoleCode,
    UserId,
)
from .role_assignment import RoleAssignment


def _norm_optional_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = value.strip()
    return s if s else None


def _norm_display_name(value: str) -> str:
    s = (value or "").strip()
    if not s:
        raise InvalidDisplayNameError("display_name is required")
    if len(s) > 100:
        raise InvalidDisplayNameError("display_name exceeds maximum length")
    return s


@dataclass
class User:
    """
    User 聚合根。

    責任：
    - 維護帳戶類型、狀態、顯示名稱、聯絡方式與身分來源（本機密碼或外部 IdP）。
    - 透過內嵌的 RoleAssignment 集合維護「承辦／管理者必須有角色」規則。
    - 強制 officer／admin 啟用 MFA。
    - 在變更後透過 _assert_invariants 確保上述規則始終成立。
    """

    user_id: UserId
    account_type: AccountType
    status: AccountStatus
    display_name: str
    created_at: datetime
    updated_at: datetime
    username: Optional[str] = None
    password_hash: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    external_identity: Optional[ExternalIdentityRef] = None
    mfa_enabled: bool = False
    last_login_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    role_assignments: List[RoleAssignment] = field(default_factory=list)

    def __post_init__(self) -> None:
        """建立或從持久層還原後立即檢查不變條件。"""
        self._assert_invariants()

    @staticmethod
    def register_applicant(
        *,
        user_id: UserId,
        display_name: str,
        email: Optional[str],
        mobile: Optional[str],
        password_hash: str,
        now: datetime,
        initial_status: AccountStatus = AccountStatus.PENDING,
    ) -> User:
        """
        UC-IAM-01：註冊申請人（領域側）。

        假設：密碼已由 App 層雜湊；領域只要求 hash 非空字串。
        Email／手機格式與重複檢查由 App + 儲存庫完成。
        """
        ph = (password_hash or "").strip()
        if not ph:
            raise InvalidCredentialInvariantError("password_hash is required for applicant password registration")

        return User(
            user_id=user_id,
            account_type=AccountType.APPLICANT,
            status=initial_status,
            display_name=_norm_display_name(display_name),
            email=_norm_optional_str(email),
            mobile=_norm_optional_str(mobile),
            username=None,
            password_hash=ph,
            external_identity=None,
            mfa_enabled=False,
            created_at=now,
            updated_at=now,
            role_assignments=[],
        )

    def assign_or_update_role(
        self,
        *,
        assignment_id: RoleAssignmentId,
        role_code: RoleCode,
        scope: AssignmentScope,
        now: datetime,
    ) -> None:
        """
        UC-IAM-04 領域部分：建立或更新一筆角色指派（業務鍵：role_code + scope）。

        呼叫端須已通過「操作者權限」檢查；audit 由 App 層記錄。
        """
        for existing in self.role_assignments:
            if existing.same_binding(role_code, scope):
                existing.assignment_id = assignment_id
                existing.touch_updated(now)
                self.updated_at = now
                self._assert_invariants()
                return

        self.role_assignments.append(
            RoleAssignment(
                assignment_id=assignment_id,
                user_id=self.user_id,
                role_code=role_code,
                scope=scope,
                created_at=now,
                updated_at=now,
            )
        )
        self.updated_at = now
        self._assert_invariants()

    def remove_role_assignment(self, assignment_id: RoleAssignmentId, now: datetime) -> None:
        """移除指定 assignment_id 的指派；移除後仍須滿足承辦／管理者不變條件。"""
        before = len(self.role_assignments)
        self.role_assignments = [a for a in self.role_assignments if a.assignment_id.value != assignment_id.value]
        if len(self.role_assignments) == before:
            return
        self.updated_at = now
        self._assert_invariants()

    def set_mfa_enabled(self, enabled: bool, now: datetime) -> None:
        """變更 MFA 旗標；officer／admin 不可關閉 MFA。"""
        if self._must_force_mfa() and not enabled:
            raise OfficerAdminRequiresMfaError("Cannot disable MFA for officer or admin accounts")
        self.mfa_enabled = enabled
        self.updated_at = now
        self._assert_invariants()

    def promote_account_type(self, new_type: AccountType, now: datetime) -> None:
        """
        將帳戶類型調整為承辦／管理者等。

        若目標為 officer／admin 且帳戶已為 ACTIVE，必須已具備角色與 MFA；
        建議流程：可先維持 PENDING、完成指派與 MFA 後再 `activate`。
        """
        self.account_type = new_type
        self.updated_at = now
        self._assert_invariants()

    def activate(self, now: datetime) -> None:
        """將帳戶標記為 ACTIVE（例如完成審核或 MFA 開通後）；承辦／管理者此時須已滿足角色與 MFA。"""
        self.status = AccountStatus.ACTIVE
        self.updated_at = now
        self._assert_invariants()

    def record_successful_login(self, now: datetime) -> None:
        """登入成功後更新最後登入時間（不含簽發 token，由 App 處理）。"""
        self.ensure_may_authenticate(now)
        self.last_login_at = now
        self.updated_at = now

    def ensure_may_authenticate(self, now: datetime) -> None:
        """
        UC-IAM-02：登入前的狀態檢查（領域側）。
        停用、鎖定、待審、已軟刪除皆不可驗證身分。
        """
        if self.deleted_at is not None:
            raise InvalidUserStateError("User has been deleted")
        if self.status != AccountStatus.ACTIVE:
            raise InvalidUserStateError(f"User status {self.status.value} does not allow authentication")

    def requires_mfa_challenge_before_tokens(self) -> bool:
        """
        登入流程中是否一定要先完成 MFA challenge 才能簽發 token。

        規則：承辦與管理者一律視為需要 MFA 步驟（與規格「強制 MFA」一致）；
        其他類型若已啟用 MFA 亦同。
        """
        if self._must_force_mfa():
            return True
        return self.mfa_enabled

    def bind_external_identity(
        self,
        *,
        provider: str,
        subject: str,
        now: datetime,
        clear_password: bool = False,
    ) -> None:
        """綁定外部 IdP 主體；可選清除本機密碼雜湊（僅允許外部登入）。"""
        self.external_identity = ExternalIdentityRef(provider=provider, subject=subject)
        if clear_password:
            self.password_hash = None
        self.updated_at = now
        self._assert_invariants()

    def set_password_hash(self, password_hash: Optional[str], now: datetime) -> None:
        """由 App 在重設密碼後寫入雜湊；須仍滿足 credential 不變條件。"""
        self.password_hash = _norm_optional_str(password_hash)
        self.updated_at = now
        self._assert_invariants()

    def soft_delete(self, now: datetime) -> None:
        """軟刪除：標記 deleted_at，阻擋後續驗證。"""
        self.deleted_at = now
        self.updated_at = now

    def _must_force_mfa(self) -> bool:
        return self.account_type in (AccountType.OFFICER, AccountType.ADMIN)

    def _assert_invariants(self) -> User:
        has_password = bool((self.password_hash or "").strip())
        has_external = self.external_identity is not None
        if not has_password and not has_external:
            raise InvalidCredentialInvariantError()

        # 規格：承辦／管理者「必須有角色」「強制 MFA」— 於 ACTIVE 時強制，PENDING 允許開通流程分段完成。
        if (
            self.account_type in (AccountType.OFFICER, AccountType.ADMIN)
            and self.status == AccountStatus.ACTIVE
        ):
            if not self.role_assignments:
                raise OfficerAdminRequiresRoleError()
            if not self.mfa_enabled:
                raise OfficerAdminRequiresMfaError()

        return self
