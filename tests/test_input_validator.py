# tests/test_input_validator.py
#
# Tests for input validation service.
# Verifies input validation, truncation, and topic parsing.
#

import pytest
from app.services.quota import InputValidator, ValidationResult


class TestInputValidator:
    # Tests for InputValidator service
    
    def test_validate_empty_input(self):
        # Test validation of empty input
        validator = InputValidator()
        
        result = validator.validate_and_prepare("")
        
        assert result.is_valid is False
        assert result.error_message is not None
        assert "empty" in result.error_message.lower()
    
    def test_validate_short_input(self):
        # Test validation of short input within limits
        validator = InputValidator()
        
        short_text = "Explain Python decorators"
        result = validator.validate_and_prepare(short_text)
        
        assert result.is_valid is True
        assert result.text == short_text
        assert result.token_count > 0
        assert result.token_count < 300
        assert result.was_truncated is False
        assert result.warning_message is None
    
    def test_validate_long_input_with_auto_truncate(self):
        # Test validation of input exceeding limit with auto-truncation
        validator = InputValidator()
        
        # Create text with more than 300 tokens
        long_text = "This is a test sentence. " * 100  # ~500+ tokens
        result = validator.validate_and_prepare(long_text, auto_truncate=True)
        
        assert result.is_valid is True
        assert len(result.text) < len(long_text)
        assert result.token_count <= 300
        assert result.was_truncated is True
        assert result.warning_message is not None
        assert "truncated" in result.warning_message.lower()
    
    def test_validate_long_input_without_auto_truncate(self):
        # Test validation of input exceeding limit without auto-truncation
        validator = InputValidator()
        
        long_text = "This is a test sentence. " * 100
        result = validator.validate_and_prepare(long_text, auto_truncate=False)
        
        assert result.is_valid is False
        assert result.text == long_text
        assert result.token_count > 300
        assert result.was_truncated is False
        assert result.error_message is not None
        assert "exceeds maximum token limit" in result.error_message
    
    def test_validate_topic_list_valid(self):
        # Test validation of valid comma-separated topics
        validator = InputValidator()
        
        topics_input = "Python, Docker, Kubernetes"
        is_valid, topics, error = validator.validate_topic_list(topics_input)
        
        assert is_valid is True
        assert len(topics) == 3
        assert "Python" in topics
        assert "Docker" in topics
        assert "Kubernetes" in topics
        assert error is None
    
    def test_validate_topic_list_with_whitespace(self):
        # Test topic validation with extra whitespace
        validator = InputValidator()
        
        topics_input = "  Python  ,   Docker   , Kubernetes  "
        is_valid, topics, error = validator.validate_topic_list(topics_input)
        
        assert is_valid is True
        assert len(topics) == 3
        assert all(not t.startswith(" ") and not t.endswith(" ") for t in topics)
    
    def test_validate_topic_list_empty(self):
        # Test validation of empty topic list
        validator = InputValidator()
        
        is_valid, topics, error = validator.validate_topic_list("")
        
        assert is_valid is False
        assert len(topics) == 0
        assert error is not None
        assert "at least one topic" in error.lower()
    
    def test_validate_topic_list_too_short(self):
        # Test validation of topics that are too short
        validator = InputValidator()
        
        topics_input = "a, b, Python"
        is_valid, topics, error = validator.validate_topic_list(topics_input)
        
        assert is_valid is False
        assert error is not None
        assert "too short" in error.lower()
    
    def test_validate_topic_list_too_long(self):
        # Test validation of topics that are too long
        validator = InputValidator()
        
        long_topic = "A" * 201
        topics_input = f"{long_topic}, Python"
        is_valid, topics, error = validator.validate_topic_list(topics_input)
        
        assert is_valid is False
        assert error is not None
        assert "too long" in error.lower()
    
    def test_validate_topic_list_too_many(self):
        # Test validation of too many topics
        validator = InputValidator()
        
        topics_input = "Topic1, Topic2, Topic3, Topic4, Topic5, Topic6"
        is_valid, topics, error = validator.validate_topic_list(topics_input)
        
        assert is_valid is False
        assert error is not None
        assert "too many" in error.lower()
        assert "maximum 5" in error.lower()
    
    def test_validation_result_properties(self):
        # Test ValidationResult properties
        result = ValidationResult(
            is_valid=True,
            text="Test text",
            token_count=10,
            was_truncated=False
        )
        
        assert result.is_valid is True
        assert result.text == "Test text"
        assert result.token_count == 10
        assert result.was_truncated is False
        assert result.warning_message is None
        assert result.error_message is None

