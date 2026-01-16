# tests/test_explanation_service.py
#
# Unit tests for ExplanationService and OutputFormatter
# Tests streaming, formatting, and topic aggregation

import pytest
from app.services.explanation import ExplanationService, OutputFormatter


class TestExplanationService:
    """Tests for ExplanationService (LLM streaming)."""
    
    @pytest.fixture
    def service(self):
        return ExplanationService()
    
    def test_explain_stream_yields_accumulated_text(self, service):
        """Test that explain_stream() yields progressively accumulated chunks."""
        chunks = list(service.explain_stream("Python"))
        
        # Should produce multiple chunks
        assert len(chunks) > 0
        
        # All chunks should be strings
        assert all(isinstance(chunk, str) for chunk in chunks)
        
        # Chunks should be progressively larger or equal
        for i in range(1, len(chunks)):
            assert len(chunks[i]) >= len(chunks[i-1])
        
        # Final output should mention Python
        assert "python" in chunks[-1].lower()
    
    def test_explain_multiple_stream_yields_topic_pairs(self, service):
        """Test explain_multiple_stream() for comma-separated topics."""
        topics_input = "Docker, Kubernetes"
        results = list(service.explain_multiple_stream(topics_input))
        
        # Should produce results
        assert len(results) > 0
        
        # Each result is a tuple (topic, accumulated_text)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
        
        # Should process both topics
        all_text = " ".join([r[1] for r in results])
        assert "docker" in all_text.lower() or "kubernetes" in all_text.lower()


class TestOutputFormatter:
    """Tests for OutputFormatter (sanitization and aggregation)."""
    
    @pytest.fixture
    def formatter(self):
        return OutputFormatter()
    
    def test_sanitize_output_removes_markdown(self, formatter):
        """Test that sanitize_output removes Markdown syntax."""
        markdown_text = "## Heading\n\n**Bold** and *italic* text with `code`"
        sanitized = formatter.sanitize_output(markdown_text)
        
        # Markdown should be removed
        assert "##" not in sanitized
        assert "**" not in sanitized
        assert "*" not in sanitized
        assert "`" not in sanitized
        
        # Content should still be there
        assert "Heading" in sanitized
        assert "Bold" in sanitized
    
    def test_sanitize_output_removes_code_blocks(self, formatter):
        """Test that sanitize_output removes code blocks."""
        text_with_code = "Some text\n```python\nprint('hello')\n```\nMore text"
        sanitized = formatter.sanitize_output(text_with_code)
        
        assert "```" not in sanitized
        assert "Some text" in sanitized
        assert "More text" in sanitized
    
    def test_parse_topics_splits_comma_separated(self, formatter):
        """Test parse_topics splits comma-separated input."""
        raw_input = "Python, Docker, React"
        topics = formatter.parse_topics(raw_input)
        
        assert len(topics) == 3
        assert "Python" in topics
        assert "Docker" in topics
        assert "React" in topics
    
    def test_parse_topics_handles_extra_whitespace(self, formatter):
        """Test parse_topics cleans whitespace."""
        raw_input = "  Python  ,   Docker   , React  "
        topics = formatter.parse_topics(raw_input)
        
        assert topics == ["Python", "Docker", "React"]
    
    def test_aggregate_topics_output_combines_topics(self, formatter):
        """Test aggregate_topics_output combines multiple topics."""
        topics = ["Python", "Docker"]
        topic_contents = {
            "Python": "Python is a programming language.",
            "Docker": "Docker is a containerization platform."
        }
        
        result = formatter.aggregate_topics_output(topics, topic_contents)
        
        assert "Python" in result
        assert "Docker" in result
        assert "programming language" in result
        assert "containerization" in result
        assert "=" * 60 in result  # Separator between topics
    
    def test_aggregate_avoids_topic_duplication(self, formatter):
        """Test aggregate_topics_output avoids duplicating topic prefix."""
        topics = ["TypeScript"]
        topic_contents = {
            "TypeScript": "TypeScript: TypeScript is a typed superset of JavaScript."
        }
        
        result = formatter.aggregate_topics_output(topics, topic_contents)
        
        # Should NOT start with "TypeScript:\n\nTypeScript:"
        assert not result.startswith("TypeScript:\n\nTypeScript:")
        # Should contain the content
        assert "typed superset" in result

