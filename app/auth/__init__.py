# app/auth/__init__.py
#
# Authentication and session management.
# Provides HF OAuth integration, multi-provider OAuth, and user session tracking.
#
# Note: oauth_providers is not exported here to avoid circular imports.
# Import directly from app.auth.oauth_providers if needed.

from app.auth.hf_auth import HFAuthService, hf_auth_service
from app.auth.session import UserSession, SessionManager, session_manager

__all__ = [
    "HFAuthService",
    "hf_auth_service",
    "UserSession",
    "SessionManager",
    "session_manager",
]

