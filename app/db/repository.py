# app/db/repository.py
#
# Repository layer for database operations.
# Provides CRUD operations for users, requests, and quotas.
#

from datetime import datetime, date
from typing import Optional, List
import sqlite3

from app.db.connection import db_manager
from app.db.models import User, RequestLog, DailyQuota, QuotaStatus, QuotaConfig


class QuotaRepository:
    # Repository for quota management operations
    
    def __init__(self):
        db_manager.initialize_schema()
        self.config = QuotaConfig()
    
    # ==================== User Operations ====================
    
    def create_user(self, user_id: str, hf_username: str) -> User:
        # Create a new user
        conn = db_manager.get_connection()
        try:
            conn.execute(
                "INSERT INTO users (user_id, hf_username) VALUES (?, ?)",
                (user_id, hf_username)
            )
            conn.commit()
            return self.get_user(user_id)
        finally:
            conn.close()
    
    def get_user(self, user_id: str) -> Optional[User]:
        # Get user by ID
        conn = db_manager.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return User(**dict(row))
            return None
        finally:
            conn.close()
    
    def get_or_create_user(self, user_id: str, hf_username: str) -> User:
        # Get user or create if not exists
        user = self.get_user(user_id)
        if not user:
            user = self.create_user(user_id, hf_username)
        return user
    
    def update_user_totals(self, user_id: str, requests_delta: int = 1, tokens_delta: int = 0):
        # Update user total counts
        conn = db_manager.get_connection()
        try:
            conn.execute(
                """UPDATE users 
                   SET total_requests = total_requests + ?,
                       total_tokens = total_tokens + ?
                   WHERE user_id = ?""",
                (requests_delta, tokens_delta, user_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    # ==================== Request Log Operations ====================
    
    def log_request(self, log: RequestLog) -> int:
        # Log a request and return its ID
        conn = db_manager.get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO request_log 
                   (user_id, timestamp, topic, rag_used, input_tokens, output_tokens, 
                    total_tokens, success, error_msg)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (log.user_id, log.timestamp, log.topic, log.rag_used,
                 log.input_tokens, log.output_tokens, log.total_tokens,
                 log.success, log.error_msg)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_user_requests(self, user_id: str, limit: int = 100) -> List[RequestLog]:
        # Get recent requests for a user
        conn = db_manager.get_connection()
        try:
            cursor = conn.execute(
                """SELECT * FROM request_log 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
            return [RequestLog(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ==================== Daily Quota Operations ====================
    
    def get_daily_quota(self, user_id: str, target_date: Optional[date] = None) -> DailyQuota:
        # Get or create daily quota for user
        if target_date is None:
            target_date = date.today()
        
        conn = db_manager.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM daily_quotas WHERE user_id = ? AND date = ?",
                (user_id, target_date)
            )
            row = cursor.fetchone()
            
            if row:
                return DailyQuota(**dict(row))
            else:
                # Create new daily quota
                conn.execute(
                    "INSERT INTO daily_quotas (user_id, date) VALUES (?, ?)",
                    (user_id, target_date)
                )
                conn.commit()
                return DailyQuota(user_id=user_id, quota_date=target_date)
        finally:
            conn.close()
    
    def update_daily_quota(self, user_id: str, requests_delta: int = 1, tokens_delta: int = 0):
        # Update daily quota counters
        today = date.today()
        conn = db_manager.get_connection()
        try:
            # Ensure quota exists
            self.get_daily_quota(user_id, today)
            
            # Update counters
            conn.execute(
                """UPDATE daily_quotas 
                   SET requests_count = requests_count + ?,
                       tokens_count = tokens_count + ?
                   WHERE user_id = ? AND date = ?""",
                (requests_delta, tokens_delta, user_id, today)
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_quota_status(self, user_id: str) -> QuotaStatus:
        # Get current quota status for user
        quota = self.get_daily_quota(user_id)
        
        return QuotaStatus(
            requests_used=quota.requests_count,
            requests_limit=self.config.daily_requests_limit,
            requests_remaining=max(0, self.config.daily_requests_limit - quota.requests_count),
            tokens_used=quota.tokens_count,
            tokens_limit=self.config.daily_tokens_limit,
            tokens_remaining=max(0, self.config.daily_tokens_limit - quota.tokens_count),
            reset_at="00:00 UTC"
        )
    
    # ==================== Cleanup Operations ====================
    
    def cleanup_old_requests(self, days_to_keep: int = 30):
        # Delete request logs older than specified days
        conn = db_manager.get_connection()
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            
            cursor = conn.execute(
                "DELETE FROM request_log WHERE timestamp < ?",
                (cutoff_date,)
            )
            conn.commit()
            print(f"🧹 Cleaned up {cursor.rowcount} old request logs")
        finally:
            conn.close()

