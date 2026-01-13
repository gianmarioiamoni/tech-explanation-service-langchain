# app/services/history/history_query_service.py
#
# Service for querying and filtering chat history
#
# Responsibilities:
# - Search history by query
# - Group history by date

from collections import defaultdict
from datetime import datetime
from typing import List, Tuple


class HistoryQueryService:
    """Service for querying and filtering chat history"""
    
    @staticmethod
    def search_history(query: str, history: List) -> List[Tuple]:
        """
        Search in chats for query (case-insensitive).
        
        Args:
            query: Search query string
            history: List of chat entries
            
        Returns:
            Filtered list of chat entries matching the query
        """
        if not query.strip():
            return history
        
        query_lower = query.strip().lower()
        results = []
        for item in history:
            topic = item[0]
            explanation = item[1]
            # Search in topic or explanation
            if query_lower in topic.lower() or query_lower in explanation.lower():
                results.append(item)
        
        print(f"🔍 Trovate {len(results)} chat per query '{query}'")
        return results
    
    @staticmethod
    def group_by_date(history: List) -> dict:
        """
        Group chats by day.
        
        Args:
            history: List of chat entries
            
        Returns:
            Dictionary with date keys and chat lists as values,
            sorted by date (newest first)
        """
        grouped = defaultdict(list)
        for item in history:
            # Support both old format (2 elements) and new format (3 elements)
            if len(item) == 3:
                topic, explanation, timestamp = item
            else:
                # Old format without timestamp
                topic, explanation = item
                timestamp = datetime.now().isoformat()
            
            # Extract date (without time)
            try:
                dt = datetime.fromisoformat(timestamp)
                date_key = dt.strftime("%Y-%m-%d")
                date_label = dt.strftime("%d/%m/%Y")
            except:
                date_key = "unknown"
                date_label = "Data sconosciuta"
            
            grouped[date_key].append({
                "topic": topic,
                "explanation": explanation,
                "timestamp": timestamp,
                "date_label": date_label
            })
        
        # Sort by date (newest first)
        sorted_grouped = dict(sorted(grouped.items(), reverse=True))
        
        # Sort chats within each date by timestamp (newest first)
        for date_key in sorted_grouped:
            sorted_grouped[date_key] = sorted(
                sorted_grouped[date_key],
                key=lambda x: x["timestamp"],
                reverse=True
            )
        
        return sorted_grouped

