# tests/test_chain.py
#
# Integration tests for the TechExplanation LCEL chain.
# These tests validate the end-to-end behavior of the chain with the real LLM.
# This approach is more appropriate for portfolio projects to demonstrate
# working integration rather than complex mocking of LangChain internals.

import pytest
from app.chains.tech_explanation_chain import tech_explanation_chain

# ------------------------------------------------------------------
# Test: invoke returns valid string response
# ------------------------------------------------------------------
def test_chain_invoke_returns_string():
    # Test that chain.invoke() returns a non-empty string.
    result = tech_explanation_chain.invoke({"topic": "REST API"})
    
    # Assert result is a string and has content
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Verify it contains some expected keywords
    assert any(word.lower() in result.lower() for word in ["api", "rest", "http", "resource"])

# ------------------------------------------------------------------
# Test: streaming produces non-empty chunks
# ------------------------------------------------------------------
def test_chain_stream_yields():
    # Test that chain.stream() yields valid string chunks.
    streamed = list(tech_explanation_chain.stream({"topic": "Docker"}))
    
    # Assert we got chunks
    assert len(streamed) > 0
    
    # Assert all chunks are strings
    assert all(isinstance(chunk, str) for chunk in streamed)
    
    # Combine chunks and verify content
    combined = "".join(streamed)
    assert len(combined.strip()) > 0
    assert any(word.lower() in combined.lower() for word in ["docker", "container", "image"])
