# ui/callbacks/auth_callbacks.py
#
# Callbacks for authentication and user session management.
# Handles user login, session initialization, and quota display updates.
#

import gradio as gr
import logging

from app.auth import hf_auth_service, SessionManager
from app.services.quota import rate_limiter
from ui.components.quota_section import format_quota_status

logger = logging.getLogger(__name__)


def initialize_user_session(request: gr.Request):
    # Initialize user session on app load
    #
    # Args:
    #     request: Gradio request object with user info
    #
    # Returns:
    #     Tuple of (user_session, quota_display_markdown)
    
    logger.info("\n" + "="*60)
    logger.info("🔐 Initializing user session")
    
    # Extract user info from request
    user_id, username = hf_auth_service.get_or_create_user(request)
    
    if not user_id or not username:
        # No authentication or dev mode
        if hf_auth_service.auth_enabled:
            logger.error("❌ Authentication failed")
            return None, _get_auth_required_message()
        else:
            # Dev mode: use test user
            logger.info("⚠️ Dev mode: using test user")
            user_id = hf_auth_service.get_dev_user_id()
            username = "test_user"
    
    # Create session
    session = SessionManager.create_session(user_id, username)
    
    # Get quota status
    try:
        quota_status = rate_limiter.get_quota_status(user_id)
        session.update_quota_status(quota_status)
        
        quota_display = format_quota_status(
            requests_used=quota_status.requests_used,
            requests_limit=quota_status.requests_limit,
            tokens_used=quota_status.tokens_used,
            tokens_limit=quota_status.tokens_limit,
            is_warning=quota_status.is_warning_level,
            is_exhausted=quota_status.is_exhausted,
            reset_at=quota_status.reset_at
        )
        
        logger.info(f"✅ Session initialized for user: {username}")
        logger.info(f"   Quota: {quota_status.requests_remaining} requests, {quota_status.tokens_remaining} tokens remaining")
        logger.info("="*60 + "\n")
        
        return session, quota_display
        
    except Exception as e:
        logger.error(f"❌ Error fetching quota status: {e}")
        return session, _get_quota_error_message()


def update_quota_display(user_session):
    # Update quota display with current status
    #
    # Args:
    #     user_session: UserSession object
    #
    # Returns:
    #     Updated quota display markdown
    
    if not user_session:
        return _get_auth_required_message()
    
    user_id = SessionManager.get_user_id_from_session(user_session)
    
    try:
        quota_status = rate_limiter.get_quota_status(user_id)
        
        # Update session
        user_session.update_quota_status(quota_status)
        
        return format_quota_status(
            requests_used=quota_status.requests_used,
            requests_limit=quota_status.requests_limit,
            tokens_used=quota_status.tokens_used,
            tokens_limit=quota_status.tokens_limit,
            is_warning=quota_status.is_warning_level,
            is_exhausted=quota_status.is_exhausted,
            reset_at=quota_status.reset_at
        )
        
    except Exception as e:
        logger.error(f"❌ Error updating quota display: {e}")
        return _get_quota_error_message()


def _get_auth_required_message() -> str:
    # Get authentication required message
    return """
### 🔐 Authentication Required

Please log in with your Hugging Face account to use this service.

**Daily Quota Limits:**
- 20 requests per day
- 10,000 tokens per day
- 300 tokens max per request input
- 500 tokens max per request output

💡 Your quota resets daily at midnight UTC.
"""


def _get_quota_error_message() -> str:
    # Get quota error message
    return """
### ⚠️ Error Loading Quota

Unable to fetch quota information. Please try refreshing the page.

If the problem persists, please contact support.
"""

