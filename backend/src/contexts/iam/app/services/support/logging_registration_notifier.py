"""LoggingRegistrationNotifierPort — 以 logger 模擬寄送（IAM_REGISTRATION_NOTIFY=1）。"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from shared.core.logger.logger import logger


class LoggingRegistrationNotifierPort:
    def send_registration_verification_notice(
        self,
        *,
        user_id: UUID,
        display_name: str,
        email: Optional[str],
        mobile: Optional[str],
    ) -> None:
        logger.info(
            "iam.registration.verification_notice",
            user_id=str(user_id),
            display_name=display_name,
            email=email or "",
            mobile=mobile or "",
        )
