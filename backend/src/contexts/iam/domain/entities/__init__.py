"""IAM domain entities (aggregate roots and nested entities)."""

from .catalog import PermissionDefinition, RoleDefinition, RolePermissionGrant
from .mfa_challenge import MfaChallenge
from .role_assignment import RoleAssignment, scope_key
from .session import Session
from .user import User

__all__ = [
    "MfaChallenge",
    "PermissionDefinition",
    "RoleAssignment",
    "RoleDefinition",
    "RolePermissionGrant",
    "Session",
    "User",
    "scope_key",
]
