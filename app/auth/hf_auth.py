# app/auth/hf_auth.py
#
# Hugging Face OAuth authentication service.
# Handles user authentication and session management for Gradio on HF Spaces.
#

from typing import Optional, Tuple
import logging
import os

from app.db import QuotaRepository

logger = logging.getLogger(__name__)


class HFAuthService:
    # Service for Hugging Face authentication integration
    
    def __init__(self, repository: Optional[QuotaRepository] = None):
        self.repository = repository or QuotaRepository()
        self.auth_enabled = self._check_auth_enabled()
    
    def _check_auth_enabled(self) -> bool:
        # Check if authentication is enabled via environment variable
        # For local dev, auth can be disabled
        enabled = os.getenv("ENABLE_AUTH", "true").lower() == "true"
        if not enabled:
            logger.warning("⚠️ Authentication is DISABLED - for development only!")
        return enabled
    
    def extract_user_info(self, request) -> Tuple[Optional[str], Optional[str]]:
        # Extract user information from Gradio request
        #
        # Args:
        #     request: Gradio request object (gr.Request)
        #
        # Returns:
        #     Tuple of (user_id, username) or (None, None) if not authenticated
        
        if request is None:
            logger.warning("No request object provided")
            return None, None
        
        try:
            # Try to get user info from request headers/context
            # Gradio with HF auth populates request.username
            username = getattr(request, "username", None)
            
            if username:
                # Use username as user_id (HF usernames are unique)
                user_id = f"hf_{username}"
                logger.info(f"✅ Authenticated user: {username} (ID: {user_id})")
                return user_id, username
            else:
                logger.warning("No username found in request")
                return None, None
                
        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
            return None, None
    
    def get_or_create_user(self, request) -> Tuple[Optional[str], Optional[str]]:
        # Get user from request and ensure it exists in database
        #
        # Args:
        #     request: Gradio request object
        #
        # Returns:
        #     Tuple of (user_id, username) or (None, None) if authentication fails
        
        user_id, username = self.extract_user_info(request)
        
        if not user_id or not username:
            if self.auth_enabled:
                logger.error("Authentication required but no user found")
                return None, None
            else:
                # Development mode: use default test user
                logger.info("Using default test user (auth disabled)")
                user_id = "test_user"
                username = "test_user"
        
        # Ensure user exists in database
        try:
            user = self.repository.get_or_create_user(user_id, username)
            logger.info(f"User ready: {user.hf_username} (total requests: {user.total_requests})")
            return user_id, username
        except Exception as e:
            logger.error(f"Failed to create/get user: {e}")
            return None, None
    
    def get_dev_user_id(self) -> str:
        # Get default user ID for development (when auth disabled)
        #
        # Returns:
        #     Development user ID
        
        dev_user_id = "test_user"
        dev_username = "test_user"
        
        # Ensure dev user exists
        self.repository.get_or_create_user(dev_user_id, dev_username)
        
        return dev_user_id


# Global instance
hf_auth_service = HFAuthService()

