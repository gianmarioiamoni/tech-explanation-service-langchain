# app/services/explanation/output_formatter.py
#
# Service for formatting and sanitizing LLM output
#
# Responsibilities:
# - Sanitize markdown from LLM output
# - Parse and validate topic inputs
# - Aggregate multiple topic outputs

import re
from typing import List


class OutputFormatter:
    # Service for formatting and sanitizing LLM output
    #
    # Args:
    #     None
    #
    # Returns:
    #     None
    
    @staticmethod
    def sanitize_output(text: str) -> str:
        # Remove markdown formatting while maintaining natural text structure.
        #
        # Args:
        #     text: Raw LLM output with markdown
        #
        # Returns:
        #     Cleaned text without markdown
        
        # Remove code blocks FIRST (```...```) to avoid conflicts with inline code
        # Use re.DOTALL to match newlines
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        
        # Remove Markdown headers (###)
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        
        # Remove bold (**text**)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        
        # Remove italic (*text*)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        
        # Remove inline code (`text`)
        text = re.sub(r"`(.*?)`", r"\1", text)
        
        # Clean multiple spaces
        text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 consecutive newlines
        text = re.sub(r" {2,}", " ", text)  # Max 1 space between words
        
        return text.strip()
    
    @staticmethod
    def parse_topics(raw_input: str) -> List[str]:
        # Parse comma-separated topics from user input.
        #
        # Args:
        #     raw_input: Raw input string with topics (e.g., "Python, Docker, React")
        #
        # Returns:
        #     List of cleaned topic strings
        
        # Split comma-separated topics and clean them
        topics = [t.strip() for t in raw_input.split(",")]
        return [t for t in topics if t]
    
    @staticmethod
    def aggregate_topics_output(topics: List[str], topic_contents: dict) -> str:
        # Aggregate multiple topics into a single output with separators.
        #
        # Args:
        #     topics: List of topic names in order
        #     topic_contents: Dictionary mapping topic name to its explanation text
        #
        # Returns:
        #     Combined output with all topics separated by visual dividers
       
        accumulated = ""
        for t in topics:
            if t in topic_contents:
                if accumulated:  # Add separator between topics
                    accumulated += f"\n\n{'='*60}\n\n"
                accumulated += f"{t}:\n\n{topic_contents[t]}"
        return accumulated

