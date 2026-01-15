# ui/callbacks/upload_callbacks.py
#
# Callbacks for document upload and RAG indexing
#
# Responsibilities:
# - Handle file uploads from the UI
# - Process supported file types (PDF, TXT, DOCX)
# - Update RAGService index for context-aware responses
# - Return status messages to the UI

import os
from pathlib import Path
from typing import List, Tuple

from app.services.rag.rag_service import RAGService

# Domain service instance
rag_service = RAGService()

# Supported file types
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".docx"]

def upload_documents(files: List[str]) -> Tuple[str, List[str]]:
    # Handle uploaded files and update RAG index
    #
    # Args:
    #     files: List of uploaded file paths from Gradio File component
    #
    # Returns:
    #     Tuple containing:
    #       - Status message for the UI
    #       - List of filenames successfully indexed

    if not files:
        return "⚠️ No files uploaded.", []

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
    return status_message, indexed_files


def clear_rag_index() -> str:
    # Clear all documents from the RAG index
    #
    # Returns:
    #     Status message for the UI

    try:
        rag_service.clear_index()
        return "🗑️ All documents removed from RAG index."
    except Exception as e:
        print(f"❌ Failed to clear RAG index: {e}")
        return f"❌ Failed to clear RAG index: {e}"
