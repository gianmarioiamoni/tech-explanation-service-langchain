# app/services/quota/quota_aware_llm.py
#
# Quota-aware LLM service wrapper.
# Integrates quota management with LLM explanation services.
#

from typing import Generator, Tuple, Optional
import logging

from app.services.quota import (
    rate_limiter, RateLimiter,
    input_validator, InputValidator,
    token_counter, TokenCounter,
    QuotaExceededError
)
from app.services.explanation import ExplanationService
from app.db import QuotaStatus

logger = logging.getLogger(__name__)


class QuotaAwareLLMService:
    # LLM service with integrated quota management
    # Wraps ExplanationService to add quota checks and tracking
    
    def __init__(
        self,
        explanation_service: Optional[ExplanationService] = None,
        rate_limiter_service: Optional[RateLimiter] = None,
        validator: Optional[InputValidator] = None
    ):
        self.explanation_service = explanation_service or ExplanationService()
        self.rate_limiter = rate_limiter_service or rate_limiter
        self.validator = validator or input_validator
        self.token_counter = token_counter
    
    def explain_with_quota(
        self,
        topic: str,
        user_id: str,
        auto_truncate: bool = True
    ) -> Generator[Tuple[str, Optional[str], Optional[QuotaStatus]], None, None]:
        # Generate explanation with quota management
        #
        # Args:
        #     topic: Technical topic to explain
        #     user_id: User identifier for quota tracking
        #     auto_truncate: Auto-truncate input if exceeds limit
        #
        # Yields:
        #     Tuple of (accumulated_text, warning_message, quota_status)
        #
        # Raises:
        #     QuotaExceededError: If user has insufficient quota
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 Quota-aware LLM request")
        logger.info(f"User: {user_id}")
        logger.info(f"Topic: {topic}")
        
        # Step 1: Validate and prepare input
        validation_result = self.validator.validate_and_prepare(
            topic,
            user_id=user_id,
            auto_truncate=auto_truncate
        )
        
        if not validation_result.is_valid:
            logger.error(f"❌ Input validation failed: {validation_result.error_message}")
            raise ValueError(validation_result.error_message)
        
        processed_topic = validation_result.text
        input_tokens = validation_result.token_count
        warning_message = validation_result.warning_message
        
        logger.info(f"✅ Input validated: {input_tokens} tokens")
        if validation_result.was_truncated:
            logger.warning(f"⚠️ Input was truncated")
        
        # Step 2: Check and reserve quota
        try:
            estimated_tokens = self.rate_limiter.estimate_total_tokens(processed_topic)
            quota_status = self.rate_limiter.check_and_reserve_quota(user_id, estimated_tokens)
            logger.info(f"✅ Quota check passed")
            logger.info(f"   Remaining: {quota_status.requests_remaining} requests, {quota_status.tokens_remaining} tokens")
        except QuotaExceededError as e:
            logger.error(f"❌ Quota exceeded: {str(e)}")
            raise
        
        # Step 3: Generate LLM output (streaming)
        logger.info(f"🤖 Calling LLM (streaming)...")
        accumulated_output = ""
        try:
            for chunk in self.explanation_service.explain_stream(processed_topic):
                accumulated_output = chunk
                # Yield chunk with warning and quota status
                yield chunk, warning_message, quota_status
            
            logger.info(f"✅ LLM generation completed")
            
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            # Log failed request
            self.rate_limiter.consume_quota(
                user_id=user_id,
                topic=processed_topic,
                input_tokens=input_tokens,
                output_tokens=0,
                rag_used=False,
                success=False,
                error_msg=str(e)
            )
            raise
        
        # Step 4: Count output tokens and consume quota
        output_tokens = self.token_counter.count_tokens(accumulated_output)
        logger.info(f"📊 Token usage: input={input_tokens}, output={output_tokens}, total={input_tokens + output_tokens}")
        
        self.rate_limiter.consume_quota(
            user_id=user_id,
            topic=processed_topic,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            rag_used=False,  # TODO: detect RAG usage
            success=True
        )
        
        # Get updated quota status
        final_quota_status = self.rate_limiter.get_quota_status(user_id)
        logger.info(f"📈 Quota consumed")
        logger.info(f"   Remaining: {final_quota_status.requests_remaining} requests, {final_quota_status.tokens_remaining} tokens")
        logger.info(f"{'='*60}\n")
        
        # Yield final status (no new text)
        yield accumulated_output, warning_message, final_quota_status
    
    def get_quota_status(self, user_id: str) -> QuotaStatus:
        # Get current quota status for user
        #
        # Args:
        #     user_id: User identifier
        #
        # Returns:
        #     Current quota status
        
        return self.rate_limiter.get_quota_status(user_id)
    
    def validate_topic(self, topic: str) -> Tuple[bool, Optional[str]]:
        # Validate a topic without consuming quota
        #
        # Args:
        #     topic: Topic to validate
        #
        # Returns:
        #     Tuple of (is_valid, error_message)
        
        validation_result = self.validator.validate_and_prepare(
            topic,
            auto_truncate=False
        )
        
        if validation_result.is_valid:
            return True, None
        return False, validation_result.error_message


# Global instance
quota_aware_llm = QuotaAwareLLMService()

