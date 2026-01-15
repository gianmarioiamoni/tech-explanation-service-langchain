# ui/callbacks/upload_callbacks.py
#
# Callbacks for document upload and RAG indexing
#
# Responsibilities:
# - Handle file uploads from the UI
# - Process supported file types (PDF, TXT, MD, DOCX)
# - Update RAGService index for context-aware responses
# - Return status messages to the UI

import os
from pathlib import Path
from typing import List, Tuple

from app.services.rag.rag_service import RAGService

# Domain service instance
rag_service = RAGService()

# Supported file types
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".docx"]

def upload_documents(files: List[str], uploaded_state: List[str]) -> Tuple[List[str], str]:
    # Handle uploaded files and update RAG index
    #
    # Args:
    #     files: List of uploaded file paths from Gradio File component
    #     uploaded_state: Current list of uploaded files (from gr.State)
    #
    # Returns:
    #     Tuple containing:
    #       - Updated list of uploaded filenames (for gr.State)
    #       - Status message for the UI

    if not files:
        return uploaded_state if uploaded_state else [], "⚠️ No files uploaded."

    indexed_files = []
    failed_files = []

    for file_path in files:
        try:
            ext = Path(file_path).suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                failed_files.append(file_path)
                continue

            # Index document in RAGService
            rag_service.add_document(file_path)
            indexed_files.append(Path(file_path).name)

        except Exception as e:
            print(f"❌ Failed to index {file_path}: {e}")
            failed_files.append(Path(file_path).name)

    # Prepare status message
    messages = []
    if indexed_files:
        messages.append(f"✅ Indexed files: {', '.join(indexed_files)}")
    if failed_files:
        messages.append(f"⚠️ Failed or unsupported files: {', '.join(failed_files)}")

    status_message = "\n".join(messages)
    
    # Update state with new files
    updated_state = (uploaded_state if uploaded_state else []) + indexed_files
    
    return updated_state, status_message


def clear_rag_index(uploaded_state: List[str]) -> Tuple[List[str], str]:
    # Clear all documents from the RAG index
    #
    # Args:
    #     uploaded_state: Current list of uploaded files (from gr.State)
    #
    # Returns:
    #     Tuple containing:
    #       - Empty list for gr.State (cleared)
    #       - Status message for the UI

    try:
        print(f"\n{'='*60}")
        print(f"🗑️ User requested: Clear RAG index")
        rag_service.clear_index()
        print(f"✅ RAG index cleared successfully")
        print(f"{'='*60}\n")
        return [], "🗑️ All documents removed from RAG index."
    except Exception as e:
        print(f"❌ Failed to clear RAG index: {e}")
        return uploaded_state, f"❌ Failed to clear RAG index: {e}"
