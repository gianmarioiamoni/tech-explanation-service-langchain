# tests/test_quota_aware_llm.py
#
# Tests for quota-aware LLM service.
# Verifies integration of quota management with LLM calls.
#

import pytest
import os
from unittest.mock import Mock, MagicMock

from app.services.quota import QuotaAwareLLMService, QuotaExceededError
from app.services.explanation import ExplanationService
from app.db import db_manager


class TestQuotaAwareLLMService:
    # Tests for QuotaAwareLLMService
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        # Setup test database before each test
        os.environ["QUOTA_DB_DIR"] = "./test_data"
        os.environ["ENABLE_AUTH"] = "false"
        db_manager.initialized = False
        db_manager.db_path = db_manager._get_db_path()
        db_manager.reset_database()
        yield
        # Cleanup
        if os.path.exists("./test_data"):
            import shutil
            shutil.rmtree("./test_data")
    
    @pytest.fixture
    def mock_explanation_service(self):
        # Create mock ExplanationService
        mock_service = Mock(spec=ExplanationService)
        # Mock streaming response
        def mock_stream(topic):
            # Simulate LLM streaming chunks
            partial = ""
            full_text = f"Explanation of {topic}: This is a test explanation."
            words = full_text.split()
            for word in words:
                partial += word + " "
                yield partial.strip()
        
        mock_service.explain_stream = mock_stream
        return mock_service
    
    def test_explain_with_quota_success(self, mock_explanation_service):
        # Test successful explanation with quota
        service = QuotaAwareLLMService(explanation_service=mock_explanation_service)
        
        # Create user
        service.rate_limiter.repository.create_user("test_user", "test_user")
        
        # Generate explanation
        chunks = list(service.explain_with_quota("Python", "test_user"))
        
        # Verify streaming worked
        assert len(chunks) > 0
        final_chunk = chunks[-1]
        text, warning, quota_status = final_chunk
        
        assert "Explanation of Python" in text
        assert quota_status is not None
        assert quota_status.requests_used == 1
        assert quota_status.tokens_used > 0
    
    def test_explain_with_quota_auto_truncate(self, mock_explanation_service):
        # Test explanation with auto-truncated input
        service = QuotaAwareLLMService(explanation_service=mock_explanation_service)
        
        # Create user
        service.rate_limiter.repository.create_user("test_user_2", "test_user_2")
        
        # Long input (will be truncated) - create >300 tokens
        long_topic = "Explain these programming concepts in detail: " + ", ".join([f"Python feature {i}" for i in range(100)])
        
        chunks = list(service.explain_with_quota(long_topic, "test_user_2", auto_truncate=True))
        
        # Should succeed with truncation
        assert len(chunks) > 0
        final_chunk = chunks[-1]
        text, warning, quota_status = final_chunk
        
        # Should have truncation warning
        assert warning is not None
        assert "truncated" in warning.lower()
        assert quota_status.requests_used == 1
    
    def test_explain_with_quota_exhausted(self, mock_explanation_service):
        # Test explanation when quota is exhausted
        service = QuotaAwareLLMService(explanation_service=mock_explanation_service)
        
        # Create user and exhaust quota
        service.rate_limiter.repository.create_user("test_user_3", "test_user_3")
        service.rate_limiter.repository.update_daily_quota("test_user_3", requests_delta=20, tokens_delta=10000)
        
        # Try to generate explanation (should fail)
        with pytest.raises(QuotaExceededError) as exc_info:
            list(service.explain_with_quota("Python", "test_user_3"))
        
        assert "quota exceeded" in str(exc_info.value).lower()
    
    def test_explain_with_invalid_input(self, mock_explanation_service):
        # Test explanation with invalid input
        service = QuotaAwareLLMService(explanation_service=mock_explanation_service)
        
        # Create user
        service.rate_limiter.repository.create_user("test_user_4", "test_user_4")
        
        # Empty input
        with pytest.raises(ValueError) as exc_info:
            list(service.explain_with_quota("", "test_user_4"))
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_explain_with_long_input_no_truncate(self, mock_explanation_service):
        # Test explanation with long input and auto_truncate=False
        service = QuotaAwareLLMService(explanation_service=mock_explanation_service)
        
        # Create user
        service.rate_limiter.repository.create_user("test_user_5", "test_user_5")
        
        # Long input (>300 tokens)
        long_topic = "Explain these programming concepts in detail: " + ", ".join([f"Python feature {i}" for i in range(100)])
        
        # Should fail validation (exceeds limit and no auto-truncate)
        with pytest.raises(ValueError) as exc_info:
            list(service.explain_with_quota(long_topic, "test_user_5", auto_truncate=False))
        
        assert "exceeds maximum token limit" in str(exc_info.value).lower()
    
    def test_get_quota_status(self):
        # Test getting quota status
        service = QuotaAwareLLMService()
        
        # Create user
        service.rate_limiter.repository.create_user("test_user_6", "test_user_6")
        
        # Get status
        status = service.get_quota_status("test_user_6")
        
        assert status.requests_remaining == 20
        assert status.tokens_remaining == 10000
        assert status.is_exhausted is False
    
    def test_validate_topic_valid(self):
        # Test validating a valid topic
        service = QuotaAwareLLMService()
        
        is_valid, error = service.validate_topic("Python decorators")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_topic_invalid(self):
        # Test validating an invalid topic
        service = QuotaAwareLLMService()
        
        # Too long topic (>300 tokens)
        long_topic = "Explain these programming concepts in detail: " + ", ".join([f"Python feature {i}" for i in range(100)])
        is_valid, error = service.validate_topic(long_topic)
        
        assert is_valid is False
        assert error is not None
        assert "exceeds maximum token limit" in error.lower()
    
    def test_quota_consumption_tracking(self, mock_explanation_service):
        # Test that quota is properly tracked across multiple requests
        service = QuotaAwareLLMService(explanation_service=mock_explanation_service)
        
        # Create user
        service.rate_limiter.repository.create_user("test_user_7", "test_user_7")
        
        # Make first request
        list(service.explain_with_quota("Topic 1", "test_user_7"))
        status1 = service.get_quota_status("test_user_7")
        
        # Make second request
        list(service.explain_with_quota("Topic 2", "test_user_7"))
        status2 = service.get_quota_status("test_user_7")
        
        # Verify cumulative consumption
        assert status2.requests_used == 2
        assert status2.tokens_used > status1.tokens_used
        assert status2.requests_remaining == 18

