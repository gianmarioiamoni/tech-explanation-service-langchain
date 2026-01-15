# app/services/rag/document_registry.py
#
# Registry for tracking uploaded RAG documents on Hugging Face Hub
#
# Responsibilities:
# - Load list of uploaded documents from HF Hub
# - Save list of uploaded documents to HF Hub
# - Add new document to registry
# - Remove document from registry
# - Persist document metadata (filename, upload_date, source)

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, upload_file


class DocumentRegistry:
    """Registry for managing uploaded RAG documents list on Hugging Face Hub"""
    
    # Configuration constants
    HF_USERNAME = "gianmarioiamoni67"
    HF_REPO = "tech-explanation-service"
    REGISTRY_FILE = "rag_documents.json"
    HF_TOKEN = None  # Uses space token if needed
    
    def __init__(self):
        self.api = HfApi()
        self._verify_hf_setup()
    
    def _verify_hf_setup(self):
        """Verify if HF Hub is accessible"""
        try:
            self.load_registry()
            print("✅ RAG Document Registry: HF Hub accessible")
        except Exception as e:
            print(f"⚠️ RAG Document Registry: HF Hub not accessible ({e})")
            print("💡 Document list will be available only in current session")
    
    def load_registry(self) -> List[Dict[str, str]]:
        """
        Load document registry from HF Hub.
        Returns empty list if registry doesn't exist.
        
        Returns:
            List of document entries: [{"filename": str, "uploaded_at": str, "source": str}, ...]
        """
        try:
            # Force download from server, not cache
            file_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.REGISTRY_FILE,
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
                force_download=True,  # Bypass local cache
            )
            
            with open(file_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
            
            print(f"✅ Loaded RAG document registry: {len(registry)} files")
            return registry
            
        except Exception as e:
            # If file doesn't exist or other error, return empty list
            if "404" in str(e) or "Entry Not Found" in str(e):
                print("📭 No existing RAG document registry found, starting fresh")
            else:
                print(f"⚠️ Could not load RAG registry: {e}")
            return []
    
    def save_registry(self, registry: List[Dict[str, str]]) -> bool:
        """
        Save document registry to HF Hub.
        
        Args:
            registry: List of document entries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save locally first
            temp_path = f"/tmp/{self.REGISTRY_FILE}"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            # Upload to HF Hub
            upload_file(
                path_or_fileobj=temp_path,
                path_in_repo=self.REGISTRY_FILE,
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
            )
            
            print(f"✅ Saved RAG document registry to HF Hub ({len(registry)} files)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save RAG registry to HF Hub: {e}")
            return False
    
    def add_document(self, filename: str, source_path: str = None) -> List[Dict[str, str]]:
        """
        Add a new document to the registry.
        
        Args:
            filename: Name of the uploaded file
            source_path: Optional full path (for metadata)
            
        Returns:
            Updated registry list
        """
        # Load current registry
        registry = self.load_registry()
        
        # Check if already exists (avoid duplicates)
        if any(doc["filename"] == filename for doc in registry):
            print(f"⚠️ Document '{filename}' already in registry, skipping")
            return registry
        
        # Add new document
        new_doc = {
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "source": source_path or filename
        }
        registry.append(new_doc)
        
        # Save updated registry
        self.save_registry(registry)
        
        print(f"✅ Added '{filename}' to RAG document registry")
        return registry
    
    def remove_document(self, filename: str) -> List[Dict[str, str]]:
        """
        Remove a document from the registry.
        
        Args:
            filename: Name of the file to remove
            
        Returns:
            Updated registry list
        """
        # Load current registry
        registry = self.load_registry()
        
        # Remove document
        original_count = len(registry)
        registry = [doc for doc in registry if doc["filename"] != filename]
        
        if len(registry) < original_count:
            self.save_registry(registry)
            print(f"✅ Removed '{filename}' from RAG document registry")
        else:
            print(f"⚠️ Document '{filename}' not found in registry")
        
        return registry
    
    def clear_registry(self) -> List[Dict[str, str]]:
        """
        Clear all documents from the registry.
        
        Returns:
            Empty list
        """
        empty_registry = []
        self.save_registry(empty_registry)
        print(f"✅ Cleared RAG document registry")
        return empty_registry
    
    def get_filenames(self) -> List[str]:
        """
        Get list of just the filenames (without metadata).
        
        Returns:
            List of filenames
        """
        registry = self.load_registry()
        return [doc["filename"] for doc in registry]
    
    def format_status(self, registry: List[Dict[str, str]]) -> str:
        """
        Format registry as a status message for UI.
        
        Args:
            registry: List of document entries
            
        Returns:
            Formatted status string
        """
        if not registry:
            return "No documents uploaded."
        
        if len(registry) == 1:
            return f"✅ 1 document uploaded:\n• {registry[0]['filename']}"
        
        # Multiple documents
        file_list = "\n".join([f"• {doc['filename']}" for doc in registry])
        return f"✅ {len(registry)} documents uploaded:\n{file_list}"

