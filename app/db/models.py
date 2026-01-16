# app/db/models.py
#
# Pydantic models for database entities.
# These models provide type safety and validation for quota system data.
#

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    # User entity model
    user_id: str
    hf_username: str
    created_at: datetime = Field(default_factory=datetime.now)
    total_requests: int = 0
    total_tokens: int = 0


class RequestLog(BaseModel):
    # Request log entry model
    id: Optional[int] = None
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    topic: str
    rag_used: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    success: bool = True
    error_msg: Optional[str] = None


class DailyQuota(BaseModel):
    # Daily quota tracking model
    user_id: str
    quota_date: date = Field(default_factory=date.today, alias="date")
    requests_count: int = 0
    tokens_count: int = 0
    
    model_config = {"populate_by_name": True}


class QuotaStatus(BaseModel):
    # User quota status (for UI display)
    requests_used: int
    requests_limit: int
    requests_remaining: int
    tokens_used: int
    tokens_limit: int
    tokens_remaining: int
    reset_at: str  # UTC midnight
    
    @property
    def requests_percent(self) -> float:
        # Percentage of requests used
        return (self.requests_used / self.requests_limit * 100) if self.requests_limit > 0 else 0
    
    @property
    def tokens_percent(self) -> float:
        # Percentage of tokens used
        return (self.tokens_used / self.tokens_limit * 100) if self.tokens_limit > 0 else 0
    
    @property
    def is_exhausted(self) -> bool:
        # Check if quota is exhausted
        return self.requests_remaining <= 0 or self.tokens_remaining <= 0
    
    @property
    def is_warning_level(self) -> bool:
        # Check if usage is at warning level (>80%)
        return self.requests_percent > 80 or self.tokens_percent > 80


class QuotaConfig(BaseModel):
    # Quota limits configuration
    daily_requests_limit: int = 20
    daily_tokens_limit: int = 10000
    max_input_tokens: int = 300
    max_output_tokens: int = 500

