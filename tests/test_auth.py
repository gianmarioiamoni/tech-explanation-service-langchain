# tests/test_auth.py
#
# Tests for authentication and session management.
# Verifies HF OAuth integration and user session handling.
#

import pytest
import os
from unittest.mock import Mock

from app.auth import HFAuthService, UserSession, SessionManager
from app.db import db_manager


class TestHFAuthService:
    # Tests for HF authentication service
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        # Setup test database before each test
        os.environ["QUOTA_DB_DIR"] = "./test_data"
        os.environ["ENABLE_AUTH"] = "false"  # Disable auth for testing
        db_manager.initialized = False
        db_manager.db_path = db_manager._get_db_path()
        db_manager.reset_database()
        yield
        # Cleanup
        if os.path.exists("./test_data"):
            import shutil
            shutil.rmtree("./test_data")
    
    def test_extract_user_info_with_username(self):
        # Test extracting user info from request with username
        auth_service = HFAuthService()
        
        # Mock Gradio request with username
        mock_request = Mock()
        mock_request.username = "test_hf_user"
        
        user_id, username = auth_service.extract_user_info(mock_request)
        
        assert user_id == "hf_test_hf_user"
        assert username == "test_hf_user"
    
    def test_extract_user_info_no_username(self):
        # Test extracting user info from request without username
        auth_service = HFAuthService()
        
        # Mock request without username
        mock_request = Mock()
        mock_request.username = None
        
        user_id, username = auth_service.extract_user_info(mock_request)
        
        assert user_id is None
        assert username is None
    
    def test_extract_user_info_no_request(self):
        # Test extracting user info with no request
        auth_service = HFAuthService()
        
        user_id, username = auth_service.extract_user_info(None)
        
        assert user_id is None
        assert username is None
    
    def test_get_or_create_user_authenticated(self):
        # Test getting or creating user when authenticated
        auth_service = HFAuthService()
        
        # Mock authenticated request
        mock_request = Mock()
        mock_request.username = "authenticated_user"
        
        user_id, username = auth_service.get_or_create_user(mock_request)
        
        # With auth disabled, should still work
        assert user_id is not None
        assert username is not None
        
        # Verify user was created in DB
        user = auth_service.repository.get_user(user_id)
        assert user is not None
        assert user.hf_username == username
    
    def test_get_or_create_user_dev_mode(self):
        # Test dev mode with auth disabled
        auth_service = HFAuthService()
        
        # Mock request without username (should use dev user)
        mock_request = Mock()
        mock_request.username = None
        
        user_id, username = auth_service.get_or_create_user(mock_request)
        
        # Should return test user in dev mode
        assert user_id == "test_user"
        assert username == "test_user"
    
    def test_get_dev_user_id(self):
        # Test getting dev user ID
        auth_service = HFAuthService()
        
        dev_user_id = auth_service.get_dev_user_id()
        
        assert dev_user_id == "test_user"
        
        # Verify dev user exists in DB
        user = auth_service.repository.get_user(dev_user_id)
        assert user is not None


class TestUserSession:
    # Tests for UserSession dataclass
    
    def test_create_session(self):
        # Test creating a user session
        session = UserSession(
            user_id="test_id",
            username="test_user",
            is_authenticated=True
        )
        
        assert session.user_id == "test_id"
        assert session.username == "test_user"
        assert session.is_authenticated is True
        assert session.quota_status is None
    
    def test_session_to_dict(self):
        # Test converting session to dictionary
        session = UserSession(
            user_id="test_id",
            username="test_user"
        )
        
        session_dict = session.to_dict()
        
        assert isinstance(session_dict, dict)
        assert session_dict["user_id"] == "test_id"
        assert session_dict["username"] == "test_user"
    
    def test_session_from_dict(self):
        # Test creating session from dictionary
        session_dict = {
            "user_id": "test_id",
            "username": "test_user",
            "is_authenticated": True,
            "quota_status": None
        }
        
        session = UserSession.from_dict(session_dict)
        
        assert session.user_id == "test_id"
        assert session.username == "test_user"
    
    def test_update_quota_status(self):
        # Test updating quota status in session
        from app.db import QuotaStatus
        
        session = UserSession(
            user_id="test_id",
            username="test_user"
        )
        
        status = QuotaStatus(
            requests_used=5,
            requests_limit=20,
            requests_remaining=15,
            tokens_used=1000,
            tokens_limit=10000,
            tokens_remaining=9000,
            reset_at="00:00 UTC"
        )
        
        session.update_quota_status(status)
        
        assert session.quota_status is not None
        assert session.quota_status["requests_used"] == 5
        assert session.quota_status["tokens_used"] == 1000


class TestSessionManager:
    # Tests for SessionManager
    
    def test_create_session(self):
        # Test creating a session via manager
        session = SessionManager.create_session("user_123", "hf_user")
        
        assert isinstance(session, UserSession)
        assert session.user_id == "user_123"
        assert session.username == "hf_user"
        assert session.is_authenticated is True
    
    def test_create_guest_session(self):
        # Test creating a guest session
        session = SessionManager.create_guest_session()
        
        assert isinstance(session, UserSession)
        assert session.user_id == "guest"
        assert session.username == "guest"
        assert session.is_authenticated is False
    
    def test_get_user_id_from_session(self):
        # Test extracting user ID from session
        session = UserSession(
            user_id="test_123",
            username="test_user"
        )
        
        user_id = SessionManager.get_user_id_from_session(session)
        assert user_id == "test_123"
    
    def test_get_user_id_from_none_session(self):
        # Test extracting user ID from None session
        user_id = SessionManager.get_user_id_from_session(None)
        assert user_id == "guest"
    
    def test_is_authenticated(self):
        # Test checking authentication status
        authenticated_session = UserSession(
            user_id="test",
            username="test",
            is_authenticated=True
        )
        
        guest_session = UserSession(
            user_id="guest",
            username="guest",
            is_authenticated=False
        )
        
        assert SessionManager.is_authenticated(authenticated_session) is True
        assert SessionManager.is_authenticated(guest_session) is False
        assert SessionManager.is_authenticated(None) is False

