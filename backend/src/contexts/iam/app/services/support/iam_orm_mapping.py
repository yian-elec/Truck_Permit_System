"""
iam_orm_mapping — ORM 列與 Domain 聚合之轉換（Application 層）。

責任：將 Infra 查詢結果組成領域物件供規則檢查；不包含持久化邏輯。
"""

from __future__ import annotations

from typing import Iterable, List
from uuid import UUID

from src.contexts.iam.domain.entities import RoleAssignment as DomainRoleAssignment
from src.contexts.iam.domain.entities import User as DomainUser
from src.contexts.iam.domain.entities.mfa_challenge import MfaChallenge as DomainMfaChallenge
from src.contexts.iam.domain.value_objects import (
    AccountStatus,
    AccountType,
    AssignmentScope,
    ExternalIdentityRef,
    MfaChallengeId,
    MfaMethod,
    RoleAssignmentId,
    RoleCode,
    UserId,
)
from src.contexts.iam.infra.schema.mfa_challenges import MfaChallenges as MfaChallengesRow
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments as RoleAssignmentsRow
from src.contexts.iam.infra.schema.users import Users as UsersRow


def map_role_assignment_row(row: RoleAssignmentsRow) -> DomainRoleAssignment:
    """單筆角色指派 ORM → 領域實體。"""
    scope = AssignmentScope(scope_type=row.scope_type, scope_id=row.scope_id)
    return DomainRoleAssignment(
        assignment_id=RoleAssignmentId(str(row.assignment_id)),
        user_id=UserId(str(row.user_id)),
        role_code=RoleCode(row.role_code),
        scope=scope,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def domain_user_from_orm(user_row: UsersRow, assignment_rows: Iterable[RoleAssignmentsRow]) -> DomainUser:
    """
    使用者 ORM + 指派集合 → User 聚合根。

    假設：資料庫狀態滿足領域不變條件；否則 __post_init__ 將拋出領域錯誤。
    """
    assigns: List[DomainRoleAssignment] = [map_role_assignment_row(r) for r in assignment_rows]
    ext: ExternalIdentityRef | None = None
    if (user_row.external_provider or "").strip() and (user_row.external_subject or "").strip():
        ext = ExternalIdentityRef(provider=user_row.external_provider, subject=user_row.external_subject)
    return DomainUser(
        user_id=UserId(str(user_row.user_id)),
        account_type=AccountType(user_row.account_type),
        status=AccountStatus(user_row.status),
        display_name=user_row.display_name,
        created_at=user_row.created_at,
        updated_at=user_row.updated_at,
        username=user_row.username,
        password_hash=user_row.password_hash,
        email=user_row.email,
        mobile=user_row.mobile,
        external_identity=ext,
        mfa_enabled=bool(user_row.mfa_enabled),
        last_login_at=user_row.last_login_at,
        deleted_at=user_row.deleted_at,
        role_assignments=assigns,
    )


def domain_mfa_from_orm(row: MfaChallengesRow) -> DomainMfaChallenge:
    """MFA 挑戰 ORM → 領域聚合。"""
    return DomainMfaChallenge(
        challenge_id=MfaChallengeId(str(row.challenge_id)),
        user_id=UserId(str(row.user_id)),
        method=MfaMethod(row.method),
        code_hash=row.code_hash,
        expires_at=row.expires_at,
        created_at=row.created_at,
        target=row.target,
        verified_at=row.verified_at,
    )


def applicant_domain_to_users_row(domain_user: DomainUser, user_uuid: UUID) -> UsersRow:
    """將註冊完成之申請人領域物件轉為 ORM 新列（僅 UC-IAM-01 使用）。"""
    return UsersRow(
        user_id=user_uuid,
        account_type=domain_user.account_type.value,
        status=domain_user.status.value,
        username=domain_user.username,
        password_hash=domain_user.password_hash,
        display_name=domain_user.display_name,
        email=domain_user.email,
        mobile=domain_user.mobile,
        external_provider=domain_user.external_identity.provider if domain_user.external_identity else None,
        external_subject=domain_user.external_identity.subject if domain_user.external_identity else None,
        mfa_enabled=domain_user.mfa_enabled,
        last_login_at=domain_user.last_login_at,
        created_at=domain_user.created_at,
        updated_at=domain_user.updated_at,
        deleted_at=domain_user.deleted_at,
    )
