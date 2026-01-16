# tests/test_quota_integration.py
#
# Integration tests for the complete quota system.
# Tests end-to-end workflows across multiple components.
#

import pytest
import os
from unittest.mock import Mock

from app.auth import HFAuthService, SessionManager
from app.services.quota import QuotaExceededError, rate_limiter, input_validator
from app.services.explanation import ExplanationService
from app.db import db_manager, QuotaRepository
from ui.callbacks.auth_callbacks import initialize_user_session, update_quota_display
from ui.components.quota_section import format_quota_status


class TestQuotaSystemIntegration:
    # Integration tests for complete quota workflows
    
    @pytest.fixture(autouse=True)
    def setup_test_env(self):
        # Setup test environment
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
    
    def test_complete_user_lifecycle(self):
        # Test complete user lifecycle: login → usage → quota exhaustion
        
        # 1. User authentication (simulate HF OAuth)
        hf_auth = HFAuthService()
        mock_request = Mock()
        mock_request.username = "test_user_lifecycle"
        
        user_id, username = hf_auth.get_or_create_user(mock_request)
        assert user_id is not None
        assert username == "test_user_lifecycle"
        
        # 2. Create session
        session = SessionManager.create_session(user_id, username)
        assert session.user_id == user_id
        
        # 3. Check initial quota
        quota_status = rate_limiter.get_quota_status(user_id)
        assert quota_status.requests_remaining == 20
        assert quota_status.tokens_remaining == 10000
        
        # 4. Make first request (validate input)
        topic = "Python basics"
        validation_result = input_validator.validate_and_prepare(topic, user_id=user_id)
        assert validation_result.is_valid
        
        # 5. Check and reserve quota
        estimated_tokens = rate_limiter.estimate_total_tokens(topic)
        quota_status = rate_limiter.check_and_reserve_quota(user_id, estimated_tokens)
        assert quota_status.requests_remaining == 20  # Not consumed yet
        
        # 6. Consume quota (simulate LLM call)
        rate_limiter.consume_quota(
            user_id=user_id,
            topic=topic,
            input_tokens=50,
            output_tokens=150,
            rag_used=False,
            success=True
        )
        
        # 7. Verify quota was consumed
        quota_status = rate_limiter.get_quota_status(user_id)
        assert quota_status.requests_used == 1
        assert quota_status.requests_remaining == 19
        assert quota_status.tokens_used == 200
        assert quota_status.tokens_remaining == 9800
        
        # 8. Exhaust quota
        for i in range(19):
            rate_limiter.consume_quota(
                user_id=user_id,
                topic=f"Topic {i}",
                input_tokens=50,
                output_tokens=150,
                rag_used=False,
                success=True
            )
        
        # 9. Verify quota exhausted
        quota_status = rate_limiter.get_quota_status(user_id)
        assert quota_status.requests_used == 20
        assert quota_status.is_exhausted
        
        # 10. Try to use exhausted quota
        with pytest.raises(QuotaExceededError):
            rate_limiter.check_and_reserve_quota(user_id, 100)
    
    def test_ui_initialization_flow(self):
        # Test UI initialization with quota display
        
        # 1. Create mock request
        mock_request = Mock()
        mock_request.username = "ui_test_user"
        
        # 2. Initialize user session (simulates UI load)
        session, quota_display = initialize_user_session(mock_request)
        
        # 3. Verify session created
        assert session is not None
        assert session.user_id is not None
        
        # 4. Verify quota display generated
        assert quota_display is not None
        assert "Quota Available" in quota_display or "20" in quota_display
        
        # 5. Make a request (consume quota)
        user_id = session.user_id
        rate_limiter.consume_quota(
            user_id=user_id,
            topic="Test topic",
            input_tokens=100,
            output_tokens=200,
            rag_used=False,
            success=True
        )
        
        # 6. Update quota display
        updated_display = update_quota_display(session)
        
        # 7. Verify display reflects updated quota
        assert "19" in updated_display or "19 remaining" in updated_display.lower()
    
    def test_input_validation_with_quota_flow(self):
        # Test input validation → quota check → consumption flow
        
        # 1. Create user
        repo = QuotaRepository()
        user_id = "validation_test_user"
        repo.create_user(user_id, "validation_test")
        
        # 2. Test valid input (within limits)
        short_topic = "Docker basics"
        validation = input_validator.validate_and_prepare(short_topic, user_id)
        assert validation.is_valid
        assert not validation.was_truncated
        
        # 3. Reserve and consume quota
        estimated = rate_limiter.estimate_total_tokens(short_topic)
        rate_limiter.check_and_reserve_quota(user_id, estimated)
        rate_limiter.consume_quota(user_id, short_topic, 50, 100, False, True)
        
        # 4. Test long input (requires truncation)
        long_topic = "Explain these programming concepts in detail: " + ", ".join([f"Python feature {i}" for i in range(100)])
        validation = input_validator.validate_and_prepare(long_topic, user_id, auto_truncate=True)
        assert validation.is_valid
        assert validation.was_truncated
        assert validation.token_count <= 300
        
        # 5. Consume quota for truncated input
        rate_limiter.consume_quota(user_id, validation.text, validation.token_count, 100, False, True)
        
        # 6. Verify both requests logged
        status = rate_limiter.get_quota_status(user_id)
        assert status.requests_used == 2
    
    def test_quota_warning_and_exhaustion_states(self):
        # Test quota status transitions: normal → warning → exhausted
        
        # 1. Create user
        user_id = "state_test_user"
        QuotaRepository().create_user(user_id, "state_test")
        
        # 2. Initial state (normal)
        status = rate_limiter.get_quota_status(user_id)
        assert not status.is_warning_level
        assert not status.is_exhausted
        
        # 3. Use 85% of quota (warning state)
        rate_limiter.repository.update_daily_quota(user_id, requests_delta=17, tokens_delta=8500)
        status = rate_limiter.get_quota_status(user_id)
        assert status.is_warning_level
        assert not status.is_exhausted
        
        # 4. Exhaust quota
        rate_limiter.repository.update_daily_quota(user_id, requests_delta=3, tokens_delta=1500)
        status = rate_limiter.get_quota_status(user_id)
        assert status.is_warning_level  # Still warning
        assert status.is_exhausted  # And exhausted
        
        # 5. Verify UI formatting reflects states
        display_warning = format_quota_status(
            17, 20, 8500, 10000, is_warning=True, is_exhausted=False
        )
        assert "⚠️" in display_warning or "Warning" in display_warning
        
        display_exhausted = format_quota_status(
            20, 20, 10000, 10000, is_warning=True, is_exhausted=True
        )
        assert "🚫" in display_exhausted or "EXHAUSTED" in display_exhausted
    
    def test_error_recovery_and_logging(self):
        # Test error handling and quota consumption for failed requests
        
        # 1. Create user
        user_id = "error_test_user"
        QuotaRepository().create_user(user_id, "error_test")
        
        # 2. Simulate failed request (still consumes quota)
        rate_limiter.consume_quota(
            user_id=user_id,
            topic="Failed topic",
            input_tokens=50,
            output_tokens=0,  # No output due to error
            rag_used=False,
            success=False,
            error_msg="Simulated API error"
        )
        
        # 3. Verify quota consumed (even for errors)
        status = rate_limiter.get_quota_status(user_id)
        assert status.requests_used == 1
        assert status.tokens_used == 50  # Only input tokens
        
        # 4. Verify error logged in database
        requests = rate_limiter.repository.get_user_requests(user_id, limit=10)
        assert len(requests) == 1
        assert requests[0].success is False
        assert requests[0].error_msg == "Simulated API error"
    
    def test_multiple_users_quota_isolation(self):
        # Test that quotas are isolated between users
        
        # 1. Create two users
        user1_id = "isolation_user1"
        user2_id = "isolation_user2"
        repo = QuotaRepository()
        repo.create_user(user1_id, "user1")
        repo.create_user(user2_id, "user2")
        
        # 2. User 1 uses quota
        rate_limiter.consume_quota(user1_id, "Topic 1", 100, 200, False, True)
        rate_limiter.consume_quota(user1_id, "Topic 2", 100, 200, False, True)
        
        # 3. Verify User 1 quota
        status1 = rate_limiter.get_quota_status(user1_id)
        assert status1.requests_used == 2
        assert status1.tokens_used == 600
        
        # 4. Verify User 2 quota unaffected
        status2 = rate_limiter.get_quota_status(user2_id)
        assert status2.requests_used == 0
        assert status2.tokens_used == 0
        
        # 5. User 2 uses different quota
        rate_limiter.consume_quota(user2_id, "Topic A", 50, 100, False, True)
        
        # 6. Verify isolation maintained
        status1_after = rate_limiter.get_quota_status(user1_id)
        status2_after = rate_limiter.get_quota_status(user2_id)
        assert status1_after.requests_used == 2
        assert status2_after.requests_used == 1

