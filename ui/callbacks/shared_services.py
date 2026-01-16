# ui/callbacks/shared_services.py
#
# Shared service instances for callbacks
#
# This module provides singleton instances of services that need to be
# shared across multiple callback modules to maintain consistent state.

from app.services.rag.rag_service import RAGService
from app.services.rag.document_registry import DocumentRegistry
from app.services.rag.chroma_persistence import ChromaPersistence

# ================================================================
# SHARED INSTANCES (Singleton Pattern)
# ================================================================
# These instances are shared across all callback modules to ensure
# consistent state for RAG functionality.
#
# Why shared?
# - RAGService: Must see the same vectorstore across all callbacks
# - DocumentRegistry: Must track the same uploaded files
# - ChromaPersistence: Must sync the same Chroma state to HF Hub
#
# Important: Import these instances (don't create new ones)
# ================================================================

# Global RAG service instance (shared across all callbacks)
rag_service = RAGService()

# Global document registry instance (shared across all callbacks)
document_registry = DocumentRegistry()

# Global Chroma persistence instance (shared across all callbacks)
chroma_persistence = ChromaPersistence()

