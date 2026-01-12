# tests/test_service_and_prompt.py
#
# This module contains unit tests for the Tech Explanation Service and
# prompt construction.
#
# Responsibilities:
# - Verify the structured prompt produces expected message types
# - Ensure the service layer returns a string response
# - Provide a safety net for future refactoring
# - Demonstrate portfolio-level engineering practice

import pytest
from app.prompts.tech_explanation_prompt import build_tech_explanation_prompt
from app.services.tech_explanation_service import TechExplanationService


# --- Prompt Tests ---
def test_prompt_message_types():
    """
    Verify that the prompt generates messages in the correct order and types:
    - SystemMessage
    - Human/AI few-shot messages
    - HumanMessage with the runtime topic
    """
    prompt = build_tech_explanation_prompt()
    topic = "ChatPromptTemplate in LangChain"
    messages = prompt.format_messages(topic=topic)

    # Check at least 3 messages are present
    assert len(messages) >= 3

    # First message should be system message
    assert "SystemMessage" in type(messages[0]).__name__

    # Last message should be human message with the topic
    assert "HumanMessage" in type(messages[-1]).__name__
    assert topic in messages[-1].content


# --- Service Tests ---
def test_service_explain_returns_string():
    """
    Verify that the TechExplanationService.explain() method:
    - returns a string
    - output is non-empty
    """
    service = TechExplanationService()
    topic = "Few-Shot Prompting"
    result = service.explain(topic)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


# Optional: Parametrized test for multiple topics
@pytest.mark.parametrize(
    "topic",
    [
        "ChatOpenAI class",
        "System, Human, AI Messages",
        "PromptTemplate class"
    ]
)
def test_service_multiple_topics(topic):
    service = TechExplanationService()
    result = service.explain(topic)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


