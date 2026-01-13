# app/services/tech_explanation_service_facade.py
#
# Facade for TechExplanationService providing backward compatibility
#
# This class maintains the same API as the original TechExplanationService
# but delegates to the new modular domain services.
#
# Use this for backward compatibility. For new code, prefer using
# the specific domain services directly.

from typing import Generator, List, Tuple, Optional

from app.services.explanation.explanation_service import ExplanationService
from app.services.explanation.output_formatter import OutputFormatter
from app.services.history.history_repository import HistoryRepository
from app.services.history.history_query_service import HistoryQueryService
from app.services.history.history_formatter import HistoryFormatter
from app.services.history.history_loader import HistoryLoader


class TechExplanationService:
    """
    Facade class for technical explanation and history management.
    
    This class provides backward compatibility with the original monolithic
    TechExplanationService by delegating to specialized domain services.
    
    For new code, consider using the domain services directly:
    - ExplanationService for LLM explanations
    - OutputFormatter for text formatting
    - HistoryRepository for persistence
    - HistoryQueryService for searching/filtering
    - HistoryFormatter for UI formatting
    - HistoryLoader for loading specific chats
    """
    
    def __init__(self):
        # Initialize domain services
        self.explanation_service = ExplanationService()
        self.output_formatter = OutputFormatter()
        self.history_repository = HistoryRepository()
        self.history_query_service = HistoryQueryService()
        self.history_formatter = HistoryFormatter()
        self.history_loader = HistoryLoader()
    
    # -------------------------------
    # Explanation methods (delegate to ExplanationService)
    # -------------------------------
    def explain_stream(self, topic: str) -> Generator[str, None, None]:
        """Generate LLM output chunk by chunk for a single topic"""
        return self.explanation_service.explain_stream(topic)
    
    def explain_multiple_stream(
        self, raw_topics: str
    ) -> Generator[Tuple[str, str], None, None]:
        """Stream explanations for multiple topics sequentially"""
        return self.explanation_service.explain_multiple_stream(raw_topics)
    
    # -------------------------------
    # Output formatting methods (delegate to OutputFormatter)
    # -------------------------------
    def _sanitize_output(self, text: str) -> str:
        """Remove markdown formatting from text"""
        return self.output_formatter.sanitize_output(text)
    
    def parse_topics(self, raw_input: str) -> List[str]:
        """Parse comma-separated topics from input"""
        return self.output_formatter.parse_topics(raw_input)
    
    def aggregate_topics_output(self, topics: List[str], topic_contents: dict) -> str:
        """Aggregate multiple topics into single output"""
        return self.output_formatter.aggregate_topics_output(topics, topic_contents)
    
    # -------------------------------
    # History persistence methods (delegate to HistoryRepository)
    # -------------------------------
    def load_history(self) -> List:
        """Load history from HF Hub"""
        return self.history_repository.load_history()
    
    def save_history(self, history: List) -> bool:
        """Save history to HF Hub"""
        return self.history_repository.save_history(history)
    
    def add_to_history(self, topic: str, explanation: str, history: List) -> List:
        """Add new chat to history with timestamp"""
        return self.history_repository.add_to_history(topic, explanation, history)
    
    def delete_from_history(self, index: int, history: List) -> List:
        """Remove chat from history by index"""
        return self.history_repository.delete_from_history(index, history)
    
    # -------------------------------
    # History query methods (delegate to HistoryQueryService)
    # -------------------------------
    def search_history(self, query: str, history: List) -> List[Tuple]:
        """Search in chats for query"""
        return self.history_query_service.search_history(query, history)
    
    def group_by_date(self, history: List) -> dict:
        """Group chats by day"""
        return self.history_query_service.group_by_date(history)
    
    # -------------------------------
    # History formatting methods (delegate to HistoryFormatter)
    # -------------------------------
    @staticmethod
    def truncate(text: str, max_len: int) -> str:
        """Truncate text to max_len characters"""
        return HistoryFormatter.truncate(text, max_len)
    
    @staticmethod
    def parse_topic_from_selection(selection: str) -> Optional[str]:
        """Extract topic from dropdown selection"""
        return HistoryFormatter.parse_topic_from_selection(selection)
    
    def create_history_choices(self, history: List, max_topic_len: int = 60) -> Tuple[List[str], Optional[str]]:
        """Create formatted choices for history dropdown"""
        return self.history_formatter.create_history_choices(history, max_topic_len)
    
    def create_delete_choices(self, history: List, max_topic_len: int = 50) -> List[str]:
        """Create formatted choices for delete dropdown"""
        return self.history_formatter.create_delete_choices(history, max_topic_len)
    
    # -------------------------------
    # History loading methods (delegate to HistoryLoader)
    # -------------------------------
    def find_chat_by_topic(self, topic_display: str, history: List) -> Optional[Tuple[str, str]]:
        """Find chat by topic (supports truncated topics)"""
        return self.history_loader.find_chat_by_topic(topic_display, history)
    
    def get_chats_by_date(self, date_str: str, history: List) -> Optional[List[dict]]:
        """Get all chats for a specific date"""
        return self.history_loader.get_chats_by_date(date_str, history)
    
    def format_chats_for_date(self, date_str: str, chats: List[dict]) -> Tuple[str, str]:
        """Format multiple chats for display"""
        return self.history_loader.format_chats_for_date(date_str, chats)

