# app/services/quota/rate_limiter.py
#
# Rate limiting service for quota management.
# Combines database tracking with token counting for API cost control.
#

from typing import Optional, Tuple
import logging

from app.db import QuotaRepository, RequestLog, QuotaStatus, QuotaConfig
from app.services.quota.token_counter import token_counter

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    # Exception raised when user exceeds their quota
    
    def __init__(self, message: str, quota_status: Optional[QuotaStatus] = None):
        super().__init__(message)
        self.quota_status = quota_status


class RateLimiter:
    # Service for enforcing rate limits on API requests
    
    def __init__(self, repository: Optional[QuotaRepository] = None):
        self.repository = repository or QuotaRepository()
        self.config = self.repository.config
    
    def check_quota(self, user_id: str) -> Tuple[bool, QuotaStatus]:
        # Check if user has quota available
        #
        # Args:
        #     user_id: Unique user identifier
        #
        # Returns:
        #     Tuple of (has_quota, quota_status)
        
        status = self.repository.get_quota_status(user_id)
        has_quota = not status.is_exhausted
        
        if not has_quota:
            logger.warning(f"User {user_id} quota exhausted: {status.requests_used}/{status.requests_limit} requests, {status.tokens_used}/{status.tokens_limit} tokens")
        
        return has_quota, status
    
    def validate_input_tokens(self, text: str, user_id: Optional[str] = None) -> Tuple[bool, int, Optional[str]]:
        # Validate that input text is within token limits
        #
        # Args:
        #     text: Input text to validate
        #     user_id: Optional user ID for logging
        #
        # Returns:
        #     Tuple of (is_valid, token_count, error_message)
        
        token_count = token_counter.count_tokens(text)
        max_tokens = self.config.max_input_tokens
        
        if token_count > max_tokens:
            error_msg = f"Input exceeds maximum token limit: {token_count} > {max_tokens}"
            if user_id:
                logger.warning(f"User {user_id} input validation failed: {error_msg}")
            return False, token_count, error_msg
        
        return True, token_count, None
    
    def estimate_total_tokens(self, input_text: str) -> int:
        # Estimate total tokens for request (input + estimated output)
        #
        # Args:
        #     input_text: User input text
        #
        # Returns:
        #     Estimated total tokens
        
        input_tokens = token_counter.count_tokens(input_text)
        # Conservative estimate: assume max output tokens
        estimated_output = self.config.max_output_tokens
        return input_tokens + estimated_output
    
    def check_and_reserve_quota(self, user_id: str, estimated_tokens: int) -> QuotaStatus:
        # Check quota and reserve tokens for upcoming request
        #
        # Args:
        #     user_id: Unique user identifier
        #     estimated_tokens: Estimated tokens for this request
        #
        # Returns:
        #     Current quota status
        #
        # Raises:
        #     QuotaExceededError: If quota is insufficient
        
        has_quota, status = self.check_quota(user_id)
        
        if not has_quota:
            raise QuotaExceededError(
                f"Daily quota exceeded. Requests: {status.requests_used}/{status.requests_limit}, "
                f"Tokens: {status.tokens_used}/{status.tokens_limit}. Resets at {status.reset_at}.",
                quota_status=status
            )
        
        # Check if estimated tokens would exceed limit
        if status.tokens_remaining < estimated_tokens:
            raise QuotaExceededError(
                f"Insufficient token quota. Need {estimated_tokens}, have {status.tokens_remaining}. "
                f"Resets at {status.reset_at}.",
                quota_status=status
            )
        
        logger.info(f"User {user_id} quota check passed: {status.requests_remaining} requests, {status.tokens_remaining} tokens remaining")
        return status
    
    def consume_quota(
        self,
        user_id: str,
        topic: str,
        input_tokens: int,
        output_tokens: int,
        rag_used: bool = False,
        success: bool = True,
        error_msg: Optional[str] = None
    ) -> int:
        # Consume quota after request completion
        #
        # Args:
        #     user_id: Unique user identifier
        #     topic: Topic that was explained
        #     input_tokens: Actual input tokens used
        #     output_tokens: Actual output tokens generated
        #     rag_used: Whether RAG was used
        #     success: Whether request was successful
        #     error_msg: Optional error message if failed
        #
        # Returns:
        #     Request log ID
        
        total_tokens = input_tokens + output_tokens
        
        # Log the request
        log = RequestLog(
            user_id=user_id,
            topic=topic,
            rag_used=rag_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            success=success,
            error_msg=error_msg
        )
        log_id = self.repository.log_request(log)
        
        # Update daily quota
        self.repository.update_daily_quota(user_id, requests_delta=1, tokens_delta=total_tokens)
        
        # Update user totals
        self.repository.update_user_totals(user_id, requests_delta=1, tokens_delta=total_tokens)
        
        logger.info(f"User {user_id} consumed quota: +1 request, +{total_tokens} tokens (input: {input_tokens}, output: {output_tokens})")
        
        return log_id
    
    def get_quota_status(self, user_id: str) -> QuotaStatus:
        # Get current quota status for user
        #
        # Args:
        #     user_id: Unique user identifier
        #
        # Returns:
        #     Current quota status
        
        return self.repository.get_quota_status(user_id)


# Global instance
rate_limiter = RateLimiter()

