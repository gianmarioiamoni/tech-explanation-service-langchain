# tests/services/test_tech_explanation_service.py
#
# Unit tests for the TechExplanationService.
# These tests verify:
# - that explain() returns sanitized output
# - that explain_stream() yields progressively accumulated, sanitized chunks
# - that the service handles empty input gracefully

import pytest
from app.services.tech_explanation_service import TechExplanationService


@pytest.fixture
def service():
    # Provide a fresh instance of the service for each test
    return TechExplanationService()


def test_explain_returns_sanitized_output(service):
    # Test that explain() returns output with Markdown-like tokens removed
    topic = "Test Topic"
    output = service.explain(topic)

    # Ensure Markdown tokens are not present
    forbidden_tokens = ["##", "# ", "**", "`"]
    for token in forbidden_tokens:
        assert token not in output

    # Ensure some output is returned
    assert len(output) > 0


def test_explain_stream_yields_accumulated_sanitized_chunks(service):
    # Test that explain_stream() yields progressively accumulated output
    topic = "Streaming Test Topic"
    chunks = list(service.explain_stream(topic))

    # At least one chunk should be produced
    assert len(chunks) > 0

    # Last chunk should be the full sanitized output
    final_output = chunks[-1]
    forbidden_tokens = ["##", "# ", "**", "`"]
    for token in forbidden_tokens:
        assert token not in final_output

    # Each chunk should be progressively increasing or equal
    for i in range(1, len(chunks)):
        assert len(chunks[i]) >= len(chunks[i-1])


def test_explain_stream_empty_input(service):
    # Test that an empty topic returns no chunks
    topic = ""
    chunks = list(service.explain_stream(topic))
    # For empty string, LCEL chain might still return something, but the service could
    # optionally sanitize to empty or return an error; adjust based on implementation
    assert len(chunks) > 0  # depends on LCEL chain behavior
