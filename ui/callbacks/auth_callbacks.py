# ui/callbacks/auth_callbacks.py
#
# Callbacks for user session management and quota display.
# No authentication required - shared demo mode with usage limits.
#

import gradio as gr
import logging

from app.auth import SessionManager
from app.services.quota import rate_limiter
from ui.components.quota_section import format_quota_status

logger = logging.getLogger(__name__)


def initialize_user_session(request: gr.Request = None):
    # Initialize user session for shared demo mode
    # All users share the same quota pool
    #
    # Args:
    #     request: Gradio request object (not used in demo mode)
    #
    # Returns:
    #     Tuple of (user_session, quota_display_markdown)
    
    logger.info("\n" + "="*60)
    logger.info("🔐 Initializing shared demo session")
    
    try:
        # Shared demo user - all users share the same quota
        user_id = "shared_demo"
        username = "demo"
        
        logger.info(f"✅ Shared demo mode - user_id: {user_id}")
        
        # Create session
        session = SessionManager.create_session(user_id, username)
        logger.info(f"✅ Session created: {session}")
        
        # Get quota status
        logger.info(f"📊 Fetching quota status for user_id: {user_id}")
        quota_status = rate_limiter.get_quota_status(user_id)
        logger.info(f"✅ Quota status: {quota_status}")
        
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
        
        logger.info(f"✅ Session initialized for shared demo")
        logger.info(f"   Quota: {quota_status.requests_remaining} requests, {quota_status.tokens_remaining} tokens remaining")
        logger.info("="*60 + "\n")
        
        return session, quota_display
        
    except Exception as e:
        logger.error(f"❌ Error initializing session: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        logger.error("="*60 + "\n")
        # Return minimal safe values
        session = SessionManager.create_session("error_user", "error_user")
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
        user_id = "shared_demo"
    else:
        user_id = SessionManager.get_user_id_from_session(user_session)
    
    try:
        quota_status = rate_limiter.get_quota_status(user_id)
        
        # Update session if available
        if user_session:
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


def _get_quota_error_message() -> str:
    # Get quota error message
    return """
### ⚠️ Error Loading Quota

Unable to fetch quota information. Please try refreshing the page.

If the problem persists, please contact support.
"""

