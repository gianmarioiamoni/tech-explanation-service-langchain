# ui/callbacks/rag_callbacks.py
#
# Callbacks for RAG initialization (document registry and vectorstore)
#
# Responsibilities:
# - Initialize document registry on app startup
# - Sync Chroma vectorstore from HF Hub on startup
# - Load persistent list of uploaded documents
# - Update UI with current document status

from typing import Tuple, List
from ui.callbacks.shared_services import (
    document_registry,
    chroma_persistence,
)  # Shared instances (singleton)


def initialize_chroma_vectorstore() -> None:
    # Initialize Chroma vectorstore by syncing from HF Hub
    # Called once on app startup, before RAG registry initialization
    #
    # Returns:
    #     None (sync happens in background)
    
    print(f"\n{'='*60}")
    print(f"🔄 Initializing Chroma vectorstore...")
    
    # Sync from HF Hub (download if exists)
    chroma_persistence.sync_from_hub()
    
    print(f"✅ Chroma vectorstore initialized")
    print(f"{'='*60}\n")


def initialize_rag_registry() -> Tuple[List[str], str]:
    # Initialize RAG document registry on app load
    #
    # Returns:
    #     Tuple containing:
    #       - List of uploaded filenames for gr.State
    #       - Status message for the UI
    
    print(f"\n{'='*60}")
    print(f"🔄 Initializing RAG document registry...")
    
    # Load registry from HF Hub
    registry = document_registry.load_registry()
    
    # Extract filenames for gr.State
    filenames = [doc["filename"] for doc in registry]
    
    # Format status message for UI
    status_message = document_registry.format_status(registry)
    
    print(f"✅ RAG registry initialized: {len(filenames)} documents")
    print(f"{'='*60}\n")
    
    return filenames, status_message

