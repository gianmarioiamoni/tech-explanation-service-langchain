# app/services/quota/input_validator.py
#
# Input validation and truncation service.
# Ensures user input complies with token limits before LLM processing.
#

from typing import Tuple, Optional
import logging

from app.services.quota.token_counter import token_counter
from app.db import QuotaConfig

logger = logging.getLogger(__name__)


class ValidationResult:
    # Result of input validation
    
    def __init__(
        self,
        is_valid: bool,
        text: str,
        token_count: int,
        was_truncated: bool = False,
        warning_message: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.text = text
        self.token_count = token_count
        self.was_truncated = was_truncated
        self.warning_message = warning_message
        self.error_message = error_message


class InputValidator:
    # Service for validating and truncating user input
    
    def __init__(self, config: Optional[QuotaConfig] = None):
        self.config = config or QuotaConfig()
        self.max_input_tokens = self.config.max_input_tokens
    
    def validate_and_prepare(
        self,
        text: str,
        user_id: Optional[str] = None,
        auto_truncate: bool = True
    ) -> ValidationResult:
        # Validate input text and optionally truncate to limits
        #
        # Args:
        #     text: User input text
        #     user_id: Optional user ID for logging
        #     auto_truncate: If True, automatically truncate to max tokens
        #
        # Returns:
        #     ValidationResult with processed text and metadata
        
        if not text or not text.strip():
            return ValidationResult(
                is_valid=False,
                text="",
                token_count=0,
                error_message="Input text cannot be empty"
            )
        
        # Count tokens in input
        token_count = token_counter.count_tokens(text)
        
        # Check if within limits
        if token_count <= self.max_input_tokens:
            logger.info(f"Input validation passed: {token_count} tokens (limit: {self.max_input_tokens})")
            return ValidationResult(
                is_valid=True,
                text=text,
                token_count=token_count
            )
        
        # Input exceeds limit
        if not auto_truncate:
            error_msg = (
                f"Input exceeds maximum token limit: {token_count} tokens "
                f"(maximum: {self.max_input_tokens}). "
                f"Please shorten your input."
            )
            logger.warning(f"User {user_id or 'unknown'}: {error_msg}")
            return ValidationResult(
                is_valid=False,
                text=text,
                token_count=token_count,
                error_message=error_msg
            )
        
        # Auto-truncate to max tokens
        truncated_text, final_tokens = token_counter.truncate_to_token_limit(
            text,
            self.max_input_tokens
        )
        
        warning_msg = (
            f"⚠️ Input was truncated from {token_count} to {final_tokens} tokens "
            f"(maximum: {self.max_input_tokens} tokens per request)."
        )
        
        logger.info(f"User {user_id or 'unknown'}: Input auto-truncated ({token_count} → {final_tokens} tokens)")
        
        return ValidationResult(
            is_valid=True,
            text=truncated_text,
            token_count=final_tokens,
            was_truncated=True,
            warning_message=warning_msg
        )
    
    def validate_topic_list(self, topics_input: str) -> Tuple[bool, list[str], Optional[str]]:
        # Validate comma-separated list of topics
        #
        # Args:
        #     topics_input: Comma-separated topics string
        #
        # Returns:
        #     Tuple of (is_valid, topics_list, error_message)
        
        if not topics_input or not topics_input.strip():
            return False, [], "Please enter at least one topic"
        
        # Split and clean topics
        topics = [t.strip() for t in topics_input.split(",") if t.strip()]
        
        if not topics:
            return False, [], "Please enter at least one valid topic"
        
        # Validate each topic
        for i, topic in enumerate(topics):
            if len(topic) < 2:
                return False, [], f"Topic '{topic}' is too short (minimum 2 characters)"
            
            if len(topic) > 200:
                return False, [], f"Topic '{topic}' is too long (maximum 200 characters)"
        
        # Check total number of topics
        max_topics = 5
        if len(topics) > max_topics:
            return False, [], f"Too many topics (maximum {max_topics}, got {len(topics)})"
        
        return True, topics, None


# Global instance
input_validator = InputValidator()

