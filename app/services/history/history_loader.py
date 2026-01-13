# app/services/history/history_loader.py
#
# Service for loading and formatting specific chats from history
#
# Responsibilities:
# - Find chat by topic (with truncation support)
# - Get all chats for a specific date
# - Format multiple chats for display

from typing import List, Optional, Tuple
from app.services.history.history_query_service import HistoryQueryService


class HistoryLoader:
    """Service for loading and formatting specific chats from history"""
    
    def __init__(self):
        self.query_service = HistoryQueryService()
    
    def find_chat_by_topic(self, topic_display: str, history: List) -> Optional[Tuple[str, str]]:
        """
        Find a chat in history by topic (supports truncated topics ending with '...').
        
        Args:
            topic_display: Topic to search for (may be truncated)
            history: List of chat entries
            
        Returns:
            Tuple of (topic, explanation) if found, None otherwise
        """
        is_truncated = topic_display.endswith("...")
        
        for item in history:
            topic = item[0]
            explanation = item[1]
            
            if is_truncated:
                # Match by prefix (without the '...')
                topic_prefix = topic_display[:-3]
                if topic.startswith(topic_prefix):
                    return topic, explanation
            else:
                # Exact match
                if topic == topic_display:
                    return topic, explanation
        
        # Try case-insensitive match as fallback
        topic_lower = topic_display.lower().replace("...", "")
        for item in history:
            topic = item[0]
            if topic.lower().startswith(topic_lower):
                return topic, item[1]
        
        return None
    
    def get_chats_by_date(self, date_str: str, history: List) -> Optional[List[dict]]:
        """
        Get all chats for a specific date.
        
        Args:
            date_str: Date string in format "DD/MM/YYYY"
            history: List of chat entries
            
        Returns:
            List of chat dicts for that date, or None if not found
        """
        grouped = self.query_service.group_by_date(history)
        
        for date_key, chats in grouped.items():
            if chats[0]["date_label"] == date_str:
                return chats
        
        return None
    
    @staticmethod
    def format_chats_for_date(date_str: str, chats: List[dict]) -> Tuple[str, str]:
        """
        Format multiple chats for display when a date is selected.
        
        Args:
            date_str: Date string in format "DD/MM/YYYY"
            chats: List of chat dicts for that date
            
        Returns:
            Tuple of (combined_topic, combined_output)
        """
        combined_output = f"📅 Chat del {date_str}\n"
        combined_output += "=" * 60 + "\n\n"
        
        for i, chat in enumerate(chats, 1):
            combined_output += f"🔹 Chat {i}: {chat['topic']}\n"
            combined_output += "─" * 60 + "\n"
            combined_output += chat['explanation'] + "\n\n"
            if i < len(chats):
                combined_output += "\n"
        
        combined_topic = f"📅 {date_str} ({len(chats)} chat)"
        return combined_topic, combined_output

