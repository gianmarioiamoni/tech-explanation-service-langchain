# tests/test_shared_services.py
#
# Unit tests for shared service instances (singleton pattern)
# Ensures consistent state across callback modules

import pytest


class TestSharedServices:
    """Tests for shared service singleton pattern."""
    
    def test_rag_service_is_singleton_across_modules(self):
        """Test that rag_service is the same instance across imports."""
        from ui.callbacks.shared_services import rag_service
        from ui.callbacks.explanation_callbacks import rag_service as rag_from_explanation
        from ui.callbacks.upload_callbacks import rag_service as rag_from_upload
        
        # All should be the exact same instance (same memory address)
        assert id(rag_service) == id(rag_from_explanation)
        assert id(rag_service) == id(rag_from_upload)
        assert id(rag_from_explanation) == id(rag_from_upload)
    
    def test_document_registry_is_singleton(self):
        """Test that document_registry is shared across modules."""
        from ui.callbacks.shared_services import document_registry
        from ui.callbacks.upload_callbacks import document_registry as reg_from_upload
        from ui.callbacks.rag_callbacks import document_registry as reg_from_rag
        
        # All should be the exact same instance
        assert id(document_registry) == id(reg_from_upload)
        assert id(document_registry) == id(reg_from_rag)
    
    def test_chroma_persistence_is_singleton(self):
        """Test that chroma_persistence is shared across modules."""
        from ui.callbacks.shared_services import chroma_persistence
        from ui.callbacks.upload_callbacks import chroma_persistence as cp_from_upload
        from ui.callbacks.rag_callbacks import chroma_persistence as cp_from_rag
        
        # All should be the exact same instance
        assert id(chroma_persistence) == id(cp_from_upload)
        assert id(chroma_persistence) == id(cp_from_rag)
    
    def test_shared_service_state_is_consistent(self):
        """Test that state changes in one module reflect in others."""
        from ui.callbacks.shared_services import rag_service
        from ui.callbacks.explanation_callbacks import rag_service as rag_from_explanation
        
        # Clear index in one module
        rag_service.clear_index()
        
        # State should be reflected in other module
        assert rag_from_explanation.has_documents() == rag_service.has_documents()
        
        # Both should report no documents
        assert rag_service.has_documents() is False
        assert rag_from_explanation.has_documents() is False

