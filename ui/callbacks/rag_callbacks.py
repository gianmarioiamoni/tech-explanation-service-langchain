# ui/callbacks/rag_callbacks.py
#
# Callbacks for RAG document registry initialization
#
# Responsibilities:
# - Initialize document registry on app startup
# - Load persistent list of uploaded documents
# - Update UI with current document status

from typing import Tuple, List
from app.services.rag.document_registry import DocumentRegistry

# Domain service instance
document_registry = DocumentRegistry()


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

