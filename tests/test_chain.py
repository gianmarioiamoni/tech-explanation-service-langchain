# tests/test_chain.py
#
# Integration tests for LCEL chains (generic and RAG).
# These tests validate end-to-end behavior with real LLM.
# Demonstrates working integration rather than complex mocking.

import pytest
from app.chains.tech_explanation_chain import tech_explanation_chain
from app.chains.rag_explanation_chain import rag_explanation_chain


class TestGenericChain:
    """Tests for the generic tech explanation chain."""
    
    def test_chain_invoke_returns_string(self):
        """Test that chain.invoke() returns a non-empty string."""
        result = tech_explanation_chain.invoke({"topic": "REST API"})
        
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        assert any(word.lower() in result.lower() 
                  for word in ["api", "rest", "http", "resource", "web"])
    
    def test_chain_stream_yields_chunks(self):
        """Test that chain.stream() yields progressive string chunks."""
        streamed = list(tech_explanation_chain.stream({"topic": "Docker"}))
        
        # Should produce multiple chunks
        assert len(streamed) > 0
        
        # All chunks should be strings
        assert all(isinstance(chunk, str) for chunk in streamed)
        
        # Combined output should mention docker concepts
        combined = "".join(streamed)
        assert len(combined.strip()) > 0
        assert any(word.lower() in combined.lower() 
                  for word in ["docker", "container", "image"])
    
    def test_chain_handles_simple_topic(self):
        """Test chain with single-word topic."""
        result = tech_explanation_chain.invoke({"topic": "Python"})
        
        assert isinstance(result, str)
        assert len(result) > 50  # Should be substantial explanation
        assert "python" in result.lower()


class TestRAGChain:
    """Tests for the RAG-enhanced explanation chain."""
    
    def test_rag_chain_requires_topic_and_context(self):
        """Test that RAG chain accepts topic + context."""
        result = rag_explanation_chain.invoke({
            "topic": "TypeScript",
            "context": "TypeScript is a superset of JavaScript that adds static types."
        })
        
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        assert "typescript" in result.lower()
    
    def test_rag_chain_stream_with_context(self):
        """Test RAG chain streaming with context."""
        streamed = list(rag_explanation_chain.stream({
            "topic": "FastAPI",
            "context": "FastAPI is a modern web framework for building APIs with Python."
        }))
        
        assert len(streamed) > 0
        combined = "".join(streamed)
        assert "fastapi" in combined.lower() or "api" in combined.lower()
