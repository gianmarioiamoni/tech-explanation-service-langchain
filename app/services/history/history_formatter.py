# app/services/history/history_formatter.py
#
# Service for formatting history data for UI display
#
# Responsibilities:
# - Format history choices for dropdown
# - Format delete choices for dropdown
# - Truncate text for display
# - Parse topic from dropdown selection

from typing import List, Tuple, Optional
from app.services.history.history_query_service import HistoryQueryService


class HistoryFormatter:
    """Service for formatting history data for UI display"""
    
    def __init__(self):
        self.query_service = HistoryQueryService()
    
    @staticmethod
    def truncate(text: str, max_len: int) -> str:
        """
        Truncate text to max_len characters, adding '...' if needed.
        
        Args:
            text: Text to truncate
            max_len: Maximum length
            
        Returns:
            Truncated text with '...' if longer than max_len
        """
        return text[:max_len] + "..." if len(text) > max_len else text
    
    @staticmethod
    def parse_topic_from_selection(selection: str) -> Optional[str]:
        """
        Extract the topic from a dropdown selection.
        Returns None if it's a date header or invalid selection.
        
        Args:
            selection: Selected text from dropdown
            
        Returns:
            Cleaned topic string or None if invalid
        """
        if not selection:
            return None
        
        # Ignore date headers (contain calendar emoji)
        if "📅" in selection:
            return None
        
        # Ignore special messages (no chats saved)
        if "📭" in selection:
            return None
        
        # Remove initial spaces (indentation from dropdown formatting)
        topic = selection.strip()
        
        # If empty after strip, it's not valid
        if not topic:
            return None
        
        return topic
    
    def create_history_choices(self, history: List, max_topic_len: int = 60) -> Tuple[List[str], Optional[str]]:
        """
        Create formatted choices for the history dropdown, grouped by date.
        
        Args:
            history: List of chat entries
            max_topic_len: Maximum length for topic display
            
        Returns:
            Tuple of (choices_list, default_value)
        """
        if not history:
            return ["📭 No chats saved"], None
        
        # Group by date
        grouped = self.query_service.group_by_date(history)
        
        choices = []
        
        for date_key, chats in grouped.items():
            date_label = chats[0]["date_label"]
            
            # Date header with calendar emoji as identifier
            date_header = f"📅 {date_label}"
            choices.append(date_header)
            
            # Chat items under the date - indented with 2 spaces
            for chat in chats:
                topic_display = self.truncate(chat["topic"], max_topic_len)
                choices.append(f"  {topic_display}")
        
        return choices, None
    
    def create_delete_choices(self, history: List, max_topic_len: int = 50) -> List[str]:
        """
        Create formatted choices for the delete dropdown with numeric IDs.
        
        Args:
            history: List of chat entries
            max_topic_len: Maximum length for topic display
            
        Returns:
            List of formatted choices with IDs (e.g., "0. Python basics")
        """
        return [f"{i}. {self.truncate(h[0], max_topic_len)}" for i, h in enumerate(history)] if history else []

