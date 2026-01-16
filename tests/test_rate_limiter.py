# tests/test_rate_limiter.py
#
# Tests for rate limiting service.
# Verifies quota checking, consumption, and enforcement.
#

import pytest
import os
from app.services.quota import RateLimiter, QuotaExceededError
from app.db import QuotaRepository, db_manager


class TestRateLimiter:
    # Tests for RateLimiter service
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        # Setup test database before each test
        os.environ["QUOTA_DB_DIR"] = "./test_data"
        db_manager.initialized = False
        db_manager.db_path = db_manager._get_db_path()
        db_manager.reset_database()
        yield
        # Cleanup
        if os.path.exists("./test_data"):
            import shutil
            shutil.rmtree("./test_data")
    
    def test_check_quota_new_user(self):
        # Test quota check for new user
        limiter = RateLimiter()
        
        # Create user
        limiter.repository.create_user("test_user_1", "hf_test_1")
        
        # Check quota (should have full quota)
        has_quota, status = limiter.check_quota("test_user_1")
        
        assert has_quota is True
        assert status.requests_remaining == 20
        assert status.tokens_remaining == 10000
    
    def test_validate_input_tokens_within_limit(self):
        # Test input validation for text within limit
        limiter = RateLimiter()
        
        short_text = "This is a short test."
        is_valid, token_count, error_msg = limiter.validate_input_tokens(short_text)
        
        assert is_valid is True
        assert token_count > 0
        assert token_count < 300
        assert error_msg is None
    
    def test_validate_input_tokens_exceeds_limit(self):
        # Test input validation for text exceeding limit
        limiter = RateLimiter()
        
        # Create text with more than 300 tokens
        long_text = "This is a test sentence. " * 100  # ~500+ tokens
        is_valid, token_count, error_msg = limiter.validate_input_tokens(long_text)
        
        assert is_valid is False
        assert token_count > 300
        assert error_msg is not None
        assert "exceeds maximum token limit" in error_msg
    
    def test_estimate_total_tokens(self):
        # Test token estimation for request
        limiter = RateLimiter()
        
        input_text = "Explain Python decorators"
        estimated = limiter.estimate_total_tokens(input_text)
        
        # Should be input tokens + max output tokens (500)
        assert estimated > 500
        assert estimated < 600
    
    def test_check_and_reserve_quota_success(self):
        # Test successful quota reservation
        limiter = RateLimiter()
        
        # Create user
        limiter.repository.create_user("test_user_2", "hf_test_2")
        
        # Reserve quota
        status = limiter.check_and_reserve_quota("test_user_2", estimated_tokens=100)
        
        assert status.requests_remaining == 20
        assert status.tokens_remaining == 10000
    
    def test_check_and_reserve_quota_exhausted(self):
        # Test quota reservation when exhausted
        limiter = RateLimiter()
        
        # Create user and exhaust quota
        limiter.repository.create_user("test_user_3", "hf_test_3")
        limiter.repository.update_daily_quota("test_user_3", requests_delta=20, tokens_delta=10000)
        
        # Try to reserve quota (should fail)
        with pytest.raises(QuotaExceededError) as exc_info:
            limiter.check_and_reserve_quota("test_user_3", estimated_tokens=100)
        
        assert "Daily quota exceeded" in str(exc_info.value)
        assert exc_info.value.quota_status is not None
    
    def test_check_and_reserve_quota_insufficient_tokens(self):
        # Test quota reservation with insufficient tokens
        limiter = RateLimiter()
        
        # Create user and use most tokens
        limiter.repository.create_user("test_user_4", "hf_test_4")
        limiter.repository.update_daily_quota("test_user_4", requests_delta=5, tokens_delta=9900)
        
        # Try to reserve more tokens than available
        with pytest.raises(QuotaExceededError) as exc_info:
            limiter.check_and_reserve_quota("test_user_4", estimated_tokens=200)
        
        assert "Insufficient token quota" in str(exc_info.value)
    
    def test_consume_quota_success(self):
        # Test quota consumption
        limiter = RateLimiter()
        
        # Create user
        limiter.repository.create_user("test_user_5", "hf_test_5")
        
        # Consume quota
        log_id = limiter.consume_quota(
            user_id="test_user_5",
            topic="Test Topic",
            input_tokens=50,
            output_tokens=150,
            rag_used=False,
            success=True
        )
        
        assert log_id > 0
        
        # Verify quota was consumed
        status = limiter.get_quota_status("test_user_5")
        assert status.requests_used == 1
        assert status.tokens_used == 200  # 50 + 150
        assert status.requests_remaining == 19
        assert status.tokens_remaining == 9800
    
    def test_consume_quota_with_error(self):
        # Test quota consumption for failed request
        limiter = RateLimiter()
        
        # Create user
        limiter.repository.create_user("test_user_6", "hf_test_6")
        
        # Consume quota for failed request
        log_id = limiter.consume_quota(
            user_id="test_user_6",
            topic="Test Topic",
            input_tokens=30,
            output_tokens=0,
            rag_used=False,
            success=False,
            error_msg="API Error"
        )
        
        assert log_id > 0
        
        # Verify quota was still consumed (even for errors)
        status = limiter.get_quota_status("test_user_6")
        assert status.requests_used == 1
        assert status.tokens_used == 30
    
    def test_multiple_requests_quota_tracking(self):
        # Test quota tracking across multiple requests
        limiter = RateLimiter()
        
        # Create user
        limiter.repository.create_user("test_user_7", "hf_test_7")
        
        # Make 3 requests
        for i in range(3):
            limiter.consume_quota(
                user_id="test_user_7",
                topic=f"Topic {i}",
                input_tokens=50,
                output_tokens=100,
                rag_used=False,
                success=True
            )
        
        # Verify cumulative usage
        status = limiter.get_quota_status("test_user_7")
        assert status.requests_used == 3
        assert status.tokens_used == 450  # 3 * (50 + 100)
        assert status.requests_remaining == 17
        assert status.tokens_remaining == 9550
    
    def test_quota_status_warning_level(self):
        # Test warning level detection
        limiter = RateLimiter()
        
        # Create user
        limiter.repository.create_user("test_user_8", "hf_test_8")
        
        # Use 17 requests (85% of 20)
        limiter.repository.update_daily_quota("test_user_8", requests_delta=17, tokens_delta=1000)
        
        status = limiter.get_quota_status("test_user_8")
        assert status.is_warning_level is True
        assert status.is_exhausted is False

