# app/services/explanation/explanation_service.py
#
# Service for generating technical explanations using LLM
#
# Responsibilities:
# - Stream LLM explanations for single topics
# - Stream LLM explanations for multiple topics sequentially

from typing import Generator, Tuple, List
from app.chains.tech_explanation_chain import tech_explanation_chain
from app.services.explanation.output_formatter import OutputFormatter


class ExplanationService:
    """Service for generating technical explanations using LLM"""
    
    def __init__(self):
        self.formatter = OutputFormatter()
    
    def explain_stream(self, topic: str) -> Generator[str, None, None]:
        """
        Generate LLM output chunk by chunk for a single topic.
        
        Args:
            topic: Technical topic to explain
            
        Yields:
            Accumulated text chunks (not sanitized during streaming)
        """
        accumulated = ""
        for chunk in tech_explanation_chain.stream({"topic": topic}):
            accumulated += chunk
            # Yield RAW accumulated text (without final sanitization)
            yield accumulated
    
    def explain_multiple_stream(
        self, raw_topics: str
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Stream explanations for multiple topics sequentially.
        Yields (topic_name, accumulated_text) for each chunk.
        
        Args:
            raw_topics: Comma-separated list of topics
            
        Yields:
            Tuple of (topic_name, accumulated_explanation_text)
        """
        topics = self.formatter.parse_topics(raw_topics)

        for topic in topics:
            accumulated = ""
            for chunk in tech_explanation_chain.stream({"topic": topic}):
                accumulated += chunk
                yield topic, accumulated

