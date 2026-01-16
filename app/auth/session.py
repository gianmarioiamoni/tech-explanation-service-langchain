# app/auth/session.py
#
# Session management for user state in Gradio.
# Manages user information and quota status across requests.
#

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import logging

from app.db import QuotaStatus

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    # User session data stored in Gradio State
    
    user_id: str
    username: str
    is_authenticated: bool = True
    quota_status: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        # Convert session to dictionary
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        # Create session from dictionary
        return cls(**data)
    
    def update_quota_status(self, status: QuotaStatus):
        # Update quota status in session
        self.quota_status = {
            "requests_used": status.requests_used,
            "requests_limit": status.requests_limit,
            "requests_remaining": status.requests_remaining,
            "tokens_used": status.tokens_used,
            "tokens_limit": status.tokens_limit,
            "tokens_remaining": status.tokens_remaining,
            "is_warning": status.is_warning_level,
            "is_exhausted": status.is_exhausted
        }


class SessionManager:
    # Manager for user sessions in Gradio
    
    @staticmethod
    def create_session(user_id: str, username: str) -> UserSession:
        # Create a new user session
        #
        # Args:
        #     user_id: Unique user identifier
        #     username: HF username
        #
        # Returns:
        #     New UserSession instance
        
        session = UserSession(
            user_id=user_id,
            username=username,
            is_authenticated=True
        )
        logger.info(f"Created session for user: {username}")
        return session
    
    @staticmethod
    def create_guest_session() -> UserSession:
        # Create a guest session (for dev/testing)
        #
        # Returns:
        #     Guest UserSession instance
        
        session = UserSession(
            user_id="guest",
            username="guest",
            is_authenticated=False
        )
        logger.warning("Created guest session (no auth)")
        return session
    
    @staticmethod
    def get_user_id_from_session(session: Optional[UserSession]) -> str:
        # Extract user ID from session
        #
        # Args:
        #     session: UserSession instance or None
        #
        # Returns:
        #     User ID or "guest" if no session
        
        if session and hasattr(session, 'user_id'):
            return session.user_id
        return "guest"
    
    @staticmethod
    def is_authenticated(session: Optional[UserSession]) -> bool:
        # Check if session is authenticated
        #
        # Args:
        #     session: UserSession instance or None
        #
        # Returns:
        #     True if authenticated, False otherwise
        
        if session and hasattr(session, 'is_authenticated'):
            return session.is_authenticated
        return False


# Global instance
session_manager = SessionManager()

