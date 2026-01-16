"""
Tests for token counting service.
Verifies accurate token counting and text truncation.
"""

import pytest
from app.services.quota import TokenCounter, token_counter


class TestTokenCounter:
    """Tests for TokenCounter service"""
    
    def test_count_tokens_simple_text(self):
        """Test token counting for simple text"""
        counter = TokenCounter()
        
        text = "Hello, world!"
        tokens = counter.count_tokens(text)
        
        # Should be approximately 3-4 tokens
        assert tokens > 0
        assert tokens < 10
    
    def test_count_tokens_empty_string(self):
        """Test token counting for empty string"""
        counter = TokenCounter()
        
        tokens = counter.count_tokens("")
        assert tokens == 0
    
    def test_count_tokens_long_text(self):
        """Test token counting for longer text"""
        counter = TokenCounter()
        
        text = "Python is a high-level programming language. " * 10
        tokens = counter.count_tokens(text)
        
        # Should be substantial (around 100+ tokens)
        assert tokens > 50
    
    def test_truncate_to_token_limit(self):
        """Test text truncation to token limit"""
        counter = TokenCounter()
        
        long_text = "This is a test sentence. " * 50  # ~150+ tokens
        max_tokens = 20
        
        truncated_text, token_count = counter.truncate_to_token_limit(long_text, max_tokens)
        
        # Truncated text should be shorter
        assert len(truncated_text) < len(long_text)
        
        # Token count should not exceed limit
        assert token_count <= max_tokens
        
        # Verify truncated text token count
        actual_tokens = counter.count_tokens(truncated_text)
        assert actual_tokens <= max_tokens
    
    def test_truncate_short_text(self):
        """Test truncation of text already within limit"""
        counter = TokenCounter()
        
        short_text = "Hello, world!"
        max_tokens = 100
        
        truncated_text, token_count = counter.truncate_to_token_limit(short_text, max_tokens)
        
        # Text should remain unchanged
        assert truncated_text == short_text
        
        # Token count should be accurate
        assert token_count == counter.count_tokens(short_text)
    
    def test_estimate_tokens_from_chars(self):
        """Test character-based token estimation"""
        counter = TokenCounter()
        
        text = "A" * 100  # 100 characters
        estimated = counter.estimate_tokens_from_chars(text)
        
        # Should estimate ~25 tokens (100 chars / 4)
        assert estimated > 20
        assert estimated < 30
    
    def test_count_tokens_for_messages(self):
        """Test token counting for chat messages"""
        counter = TokenCounter()
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"}
        ]
        
        tokens = counter.count_tokens_for_messages(messages)
        
        # Should include content tokens + formatting overhead
        assert tokens > 10
        assert tokens < 50
    
    def test_count_tokens_for_empty_messages(self):
        """Test token counting for empty message list"""
        counter = TokenCounter()
        
        tokens = counter.count_tokens_for_messages([])
        assert tokens == 0
    
    def test_global_token_counter_instance(self):
        """Test that global instance works"""
        text = "Test text for global instance"
        tokens = token_counter.count_tokens(text)
        
        assert tokens > 0

