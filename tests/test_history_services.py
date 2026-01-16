# tests/test_history_services.py
#
# Unit tests for History domain services
# Tests history persistence, formatting, querying, and loading

import pytest
from datetime import datetime
from app.services.history import (
    HistoryRepository,
    HistoryFormatter,
    HistoryQueryService,
    HistoryLoader
)


class TestHistoryFormatter:
    """Tests for HistoryFormatter (UI formatting logic)."""
    
    @pytest.fixture
    def formatter(self):
        return HistoryFormatter()
    
    def test_truncate_shortens_long_text(self, formatter):
        """Test truncate() shortens text longer than max_len."""
        long_text = "This is a very long text " * 10
        truncated = formatter.truncate(long_text, max_len=50)
        
        assert len(truncated) <= 53  # 50 + "..."
        assert truncated.endswith("...")
    
    def test_truncate_preserves_short_text(self, formatter):
        """Test truncate() preserves text shorter than max_len."""
        short_text = "Short text"
        truncated = formatter.truncate(short_text, max_len=50)
        
        assert truncated == short_text
        assert not truncated.endswith("...")
    
    def test_parse_topic_from_selection_extracts_topic(self, formatter):
        """Test parse_topic_from_selection extracts topic from formatted string."""
        # Format: "   Topic name"
        selection = "   Python Decorators"
        topic = formatter.parse_topic_from_selection(selection)
        
        assert topic == "Python Decorators"
    
    def test_parse_topic_from_selection_ignores_date_headers(self, formatter):
        """Test parse_topic_from_selection returns None for date headers."""
        date_header = "📅 16/01/2026"
        topic = formatter.parse_topic_from_selection(date_header)
        
        assert topic is None
    
    def test_create_history_choices_generates_dropdown_choices(self, formatter):
        """Test create_history_choices generates formatted choices."""
        history = [
            ("Python", "Python is...", datetime.now().isoformat()),
            ("Docker", "Docker is...", datetime.now().isoformat())
        ]
        
        choices, value = formatter.create_history_choices(history)
        
        # Should create choices list
        assert isinstance(choices, list)
        # Should include topics
        assert any("Python" in str(c) for c in choices)
        assert any("Docker" in str(c) for c in choices)
    
    def test_create_delete_choices_formats_for_deletion(self, formatter):
        """Test create_delete_choices formats history for delete dropdown."""
        history = [
            ("Python", "Python is...", datetime.now().isoformat()),
            ("Docker", "Docker is...", datetime.now().isoformat())
        ]
        
        choices = formatter.create_delete_choices(history)
        
        # Should format as "IDX. topic"
        assert len(choices) == 2
        assert choices[0].startswith("0.")
        assert choices[1].startswith("1.")


class TestHistoryQueryService:
    """Tests for HistoryQueryService (search and filtering)."""
    
    @pytest.fixture
    def query_service(self):
        return HistoryQueryService()
    
    def test_search_history_finds_matching_topics(self, query_service):
        """Test search_history finds topics containing query."""
        history = [
            ("Python Basics", "Content...", datetime.now().isoformat()),
            ("Docker Containers", "Content...", datetime.now().isoformat()),
            ("Kubernetes Pods", "Content...", datetime.now().isoformat())
        ]
        
        results = query_service.search_history("Python", history)
        
        assert len(results) == 1
        assert results[0][0] == "Python Basics"
    
    def test_search_history_is_case_insensitive(self, query_service):
        """Test search is case insensitive."""
        history = [
            ("Python Basics", "Content...", datetime.now().isoformat())
        ]
        
        results = query_service.search_history("python", history)
        assert len(results) == 1
        
        results = query_service.search_history("PYTHON", history)
        assert len(results) == 1
    
    def test_search_history_returns_empty_for_no_match(self, query_service):
        """Test search returns empty list when no matches."""
        history = [
            ("Python Basics", "Content...", datetime.now().isoformat())
        ]
        
        results = query_service.search_history("Nonexistent", history)
        assert len(results) == 0
    
    def test_group_by_date_groups_chats_by_day(self, query_service):
        """Test group_by_date groups chats by creation date."""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        history = [
            ("Topic1", "Content1", today.isoformat()),
            ("Topic2", "Content2", today.isoformat()),
            ("Topic3", "Content3", yesterday.isoformat())
        ]
        
        grouped = query_service.group_by_date(history)
        
        # Should return a dictionary
        assert isinstance(grouped, dict)
        
        # Should have 2 date groups
        assert len(grouped) == 2
        
        # Each value should be a list of chats
        for date_str, chats in grouped.items():
            assert isinstance(date_str, str)
            assert isinstance(chats, list)


class TestHistoryLoader:
    """Tests for HistoryLoader (loading specific chats)."""
    
    @pytest.fixture
    def loader(self):
        return HistoryLoader()
    
    def test_find_chat_by_topic_returns_matching_chat(self, loader):
        """Test find_chat_by_topic finds chat by topic name."""
        history = [
            ("Python", "Python content...", datetime.now().isoformat()),
            ("Docker", "Docker content...", datetime.now().isoformat())
        ]
        
        result = loader.find_chat_by_topic("Python", history)
        
        assert result is not None
        topic, content = result
        assert topic == "Python"
        assert "Python content" in content
    
    def test_find_chat_by_topic_returns_none_for_no_match(self, loader):
        """Test find_chat_by_topic returns None when not found."""
        history = [
            ("Python", "Python content...", datetime.now().isoformat())
        ]
        
        result = loader.find_chat_by_topic("Nonexistent", history)
        assert result is None
    
    def test_get_chats_by_date_returns_chats_for_date(self, loader):
        """Test get_chats_by_date returns chats for specific date."""
        today = datetime.now()
        date_str = today.strftime("%d/%m/%Y")
        
        history = [
            ("Topic1", "Content1", today.isoformat()),
            ("Topic2", "Content2", today.isoformat())
        ]
        
        chats = loader.get_chats_by_date(date_str, history)
        
        assert len(chats) == 2
    
    def test_format_chats_for_date_combines_chats(self, loader):
        """Test format_chats_for_date combines multiple chats."""
        chats = [
            {"topic": "Topic1", "explanation": "Content1", "timestamp": datetime.now().isoformat()},
            {"topic": "Topic2", "explanation": "Content2", "timestamp": datetime.now().isoformat()}
        ]
        
        combined_topic, combined_output = loader.format_chats_for_date("16/01/2026", chats)
        
        # combined_topic is the date, not individual topics
        assert "16/01/2026" in combined_topic
        assert "2 chat" in combined_topic
        
        # combined_output should contain both topics and content
        assert "Topic1" in combined_output
        assert "Topic2" in combined_output
        assert "Content1" in combined_output
        assert "Content2" in combined_output

