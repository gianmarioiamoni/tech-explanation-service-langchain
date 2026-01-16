"""
Tests for quota database layer.
Verifies CRUD operations and quota tracking functionality.
"""

import pytest
import os
from datetime import datetime, date
from app.db import QuotaRepository, RequestLog, db_manager


class TestQuotaRepository:
    """Tests for QuotaRepository"""
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Setup test database before each test"""
        # Use test database
        os.environ["QUOTA_DB_DIR"] = "./test_data"
        db_manager.initialized = False
        db_manager.db_path = db_manager._get_db_path()
        db_manager.reset_database()
        yield
        # Cleanup
        if os.path.exists("./test_data"):
            import shutil
            shutil.rmtree("./test_data")
    
    def test_create_and_get_user(self):
        """Test user creation and retrieval"""
        repo = QuotaRepository()
        
        # Create user
        user = repo.create_user("test_user_1", "hf_test_user")
        
        assert user.user_id == "test_user_1"
        assert user.hf_username == "hf_test_user"
        assert user.total_requests == 0
        assert user.total_tokens == 0
        
        # Get user
        retrieved_user = repo.get_user("test_user_1")
        assert retrieved_user is not None
        assert retrieved_user.user_id == user.user_id
    
    def test_get_or_create_user(self):
        """Test get_or_create_user functionality"""
        repo = QuotaRepository()
        
        # First call creates
        user1 = repo.get_or_create_user("test_user_2", "hf_test_user_2")
        assert user1.user_id == "test_user_2"
        
        # Second call retrieves
        user2 = repo.get_or_create_user("test_user_2", "hf_test_user_2")
        assert user2.user_id == user1.user_id
    
    def test_log_request(self):
        """Test request logging"""
        repo = QuotaRepository()
        
        # Create user first
        repo.create_user("test_user_3", "hf_test_user_3")
        
        # Log request
        log = RequestLog(
            user_id="test_user_3",
            topic="Test Topic",
            rag_used=False,
            input_tokens=10,
            output_tokens=50,
            total_tokens=60,
            success=True
        )
        
        log_id = repo.log_request(log)
        assert log_id > 0
        
        # Retrieve requests
        requests = repo.get_user_requests("test_user_3")
        assert len(requests) == 1
        assert requests[0].topic == "Test Topic"
        assert requests[0].total_tokens == 60
    
    def test_daily_quota_tracking(self):
        """Test daily quota creation and updates"""
        repo = QuotaRepository()
        
        # Create user
        repo.create_user("test_user_4", "hf_test_user_4")
        
        # Get initial quota (should be created)
        quota1 = repo.get_daily_quota("test_user_4")
        assert quota1.requests_count == 0
        assert quota1.tokens_count == 0
        assert quota1.quota_date == date.today()
        
        # Update quota
        repo.update_daily_quota("test_user_4", requests_delta=1, tokens_delta=100)
        
        # Verify update
        quota2 = repo.get_daily_quota("test_user_4")
        assert quota2.requests_count == 1
        assert quota2.tokens_count == 100
    
    def test_quota_status(self):
        """Test quota status calculation"""
        repo = QuotaRepository()
        
        # Create user
        repo.create_user("test_user_5", "hf_test_user_5")
        
        # Get initial status
        status = repo.get_quota_status("test_user_5")
        
        assert status.requests_used == 0
        assert status.requests_limit == 20
        assert status.requests_remaining == 20
        assert status.tokens_used == 0
        assert status.tokens_limit == 10000
        assert status.tokens_remaining == 10000
        assert not status.is_exhausted
        assert not status.is_warning_level
        
        # Update quota to warning level
        repo.update_daily_quota("test_user_5", requests_delta=17, tokens_delta=8500)
        
        status = repo.get_quota_status("test_user_5")
        assert status.requests_used == 17
        assert status.tokens_used == 8500
        assert status.is_warning_level
        assert not status.is_exhausted
        
        # Exhaust quota
        repo.update_daily_quota("test_user_5", requests_delta=3, tokens_delta=1500)
        
        status = repo.get_quota_status("test_user_5")
        assert status.is_exhausted

