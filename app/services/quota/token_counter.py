# app/services/quota/token_counter.py
#
# Token counting service using tiktoken.
# Provides accurate token counting for OpenAI models to prevent quota overruns.
#

import tiktoken
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TokenCounter:
    # Service for counting tokens in text using tiktoken
    
    # Token counting defaults
    DEFAULT_MODEL = "gpt-4o-mini"
    CHARS_PER_TOKEN_ESTIMATE = 4  # Conservative estimate for pre-checks
    
    def __init__(self, model: str = DEFAULT_MODEL):
        # Initialize token counter for specific model
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        # Count tokens in text using tiktoken.
        #
        # Args:
        #     text: Input text to count tokens for
        #
        # Returns:
        #     Number of tokens in the text
        
        if not text:
            return 0
        
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to character-based estimate
            return self.estimate_tokens_from_chars(text)
    
    def estimate_tokens_from_chars(self, text: str) -> int:
        # Estimate token count from character count.
        # Conservative estimate: 1 token per 4 characters.
        #
        # Args:
        #     text: Input text
        #
        # Returns:
        #     Estimated token count
        
        if not text:
            return 0
        return len(text) // self.CHARS_PER_TOKEN_ESTIMATE + 1
    
    def truncate_to_token_limit(self, text: str, max_tokens: int) -> tuple[str, int]:
        # Truncate text to fit within token limit.
        #
        # Args:
        #     text: Input text to truncate
        #     max_tokens: Maximum number of tokens allowed
        #
        # Returns:
        #     Tuple of (truncated_text, actual_token_count)
        
        if not text:
            return "", 0
        
        try:
            tokens = self.encoding.encode(text)
            
            if len(tokens) <= max_tokens:
                return text, len(tokens)
            
            # Truncate tokens and decode back to text
            truncated_tokens = tokens[:max_tokens]
            truncated_text = self.encoding.decode(truncated_tokens)
            
            logger.info(f"Truncated text from {len(tokens)} to {max_tokens} tokens")
            return truncated_text, max_tokens
            
        except Exception as e:
            logger.error(f"Error truncating text: {e}")
            # Fallback: character-based truncation
            estimated_chars = max_tokens * self.CHARS_PER_TOKEN_ESTIMATE
            return text[:estimated_chars], self.count_tokens(text[:estimated_chars])
    
    def count_tokens_for_messages(self, messages: list[dict]) -> int:
        # Count tokens for a list of chat messages.
        # Accounts for message formatting overhead.
        #
        # Args:
        #     messages: List of message dicts with 'role' and 'content'
        #
        # Returns:
        #     Total token count including formatting overhead
        
        if not messages:
            return 0
        
        total_tokens = 0
        
        # Formatting overhead per message
        tokens_per_message = 3  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = 1  # If there's a name, the role is omitted
        
        for message in messages:
            total_tokens += tokens_per_message
            for key, value in message.items():
                if isinstance(value, str):
                    total_tokens += self.count_tokens(value)
                if key == "name":
                    total_tokens += tokens_per_name
        
        total_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>
        
        return total_tokens


# Global instance
token_counter = TokenCounter()

