# app/services/rag/chroma_persistence.py
#
# Service for persisting Chroma vectorstore to Hugging Face Hub
#
# Responsibilities:
# - Upload chroma_db/ directory to HF Hub
# - Download chroma_db/ directory from HF Hub
# - Sync local vectorstore with remote storage
# - Handle compressed archives for efficient transfer

import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Optional
from huggingface_hub import HfApi, hf_hub_download, upload_file


class ChromaPersistence:
    # Service for managing Chroma vectorstore persistence on Hugging Face Hub
    #
    # Strategy: Compress chroma_db/ to .tar.gz, upload to HF Hub
    # On startup: Download .tar.gz, extract to chroma_db/
    
    # Configuration constants
    HF_USERNAME = "gianmarioiamoni67"
    HF_REPO = "tech-explanation-service"
    CHROMA_DIR = "./chroma_db"
    CHROMA_ARCHIVE = "chroma_db.tar.gz"
    HF_TOKEN = None  # Uses space token if needed
    
    def __init__(self):
        self.api = HfApi()
        self._verify_hf_setup()
    
    def _verify_hf_setup(self):
        # Verify if HF Hub is accessible
        try:
            # Try to check if vectorstore exists on Hub
            exists = self.exists_on_hub()
            if exists:
                print("✅ Chroma Persistence: HF Hub accessible, vectorstore found")
            else:
                print("✅ Chroma Persistence: HF Hub accessible, no existing vectorstore")
        except Exception as e:
            print(f"⚠️ Chroma Persistence: HF Hub not accessible ({e})")
            print("💡 Vectorstore will be local only")
    
    def exists_on_hub(self) -> bool:
        # Check if vectorstore archive exists on HF Hub
        #
        # Returns:
        #     True if archive exists, False otherwise
        
        try:
            # Try to get file info
            files = self.api.list_repo_files(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
            )
            return self.CHROMA_ARCHIVE in files
        except Exception as e:
            print(f"⚠️ Could not check HF Hub for vectorstore: {e}")
            return False
    
    def _compress_chroma_dir(self, output_path: str) -> bool:
        # Compress chroma_db/ directory to .tar.gz
        #
        # Args:
        #     output_path: Path where to save the .tar.gz archive
        #
        # Returns:
        #     True if successful, False otherwise
        
        if not os.path.exists(self.CHROMA_DIR):
            print(f"⚠️ Chroma directory not found: {self.CHROMA_DIR}")
            return False
        
        try:
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(self.CHROMA_DIR, arcname="chroma_db")
            
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Compressed chroma_db to {output_path} ({size_mb:.2f} MB)")
            return True
        except Exception as e:
            print(f"❌ Failed to compress chroma_db: {e}")
            return False
    
    def _extract_chroma_archive(self, archive_path: str) -> bool:
        # Extract .tar.gz archive to local chroma_db/ directory
        #
        # Args:
        #     archive_path: Path to the .tar.gz archive
        #
        # Returns:
        #     True if successful, False otherwise
        
        try:
            # Remove existing chroma_db if present
            if os.path.exists(self.CHROMA_DIR):
                shutil.rmtree(self.CHROMA_DIR)
                print(f"🗑️ Removed existing local chroma_db")
            
            # Extract archive
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(".")
            
            print(f"✅ Extracted chroma_db from {archive_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to extract chroma_db: {e}")
            return False
    
    def upload_vectorstore(self) -> bool:
        # Upload local chroma_db/ to HF Hub
        #
        # Returns:
        #     True if successful, False otherwise
        
        print(f"\n{'='*60}")
        print(f"☁️ Uploading vectorstore to HF Hub...")
        
        # Check if chroma_db exists locally
        if not os.path.exists(self.CHROMA_DIR):
            print(f"⚠️ No local chroma_db to upload")
            print(f"{'='*60}\n")
            return False
        
        # Create temporary archive
        temp_archive = os.path.join(tempfile.gettempdir(), self.CHROMA_ARCHIVE)
        
        try:
            # Compress
            if not self._compress_chroma_dir(temp_archive):
                return False
            
            # Upload to HF Hub
            upload_file(
                path_or_fileobj=temp_archive,
                path_in_repo=self.CHROMA_ARCHIVE,
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
            )
            
            size_mb = os.path.getsize(temp_archive) / (1024 * 1024)
            print(f"✅ Uploaded vectorstore to HF Hub ({size_mb:.2f} MB)")
            print(f"{'='*60}\n")
            
            # Cleanup temp file
            os.remove(temp_archive)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload vectorstore to HF Hub: {e}")
            print(f"{'='*60}\n")
            
            # Cleanup temp file if exists
            if os.path.exists(temp_archive):
                os.remove(temp_archive)
            
            return False
    
    def download_vectorstore(self) -> bool:
        # Download chroma_db/ from HF Hub to local directory
        #
        # Returns:
        #     True if successful, False otherwise
        
        print(f"\n{'='*60}")
        print(f"☁️ Downloading vectorstore from HF Hub...")
        
        # Check if exists on Hub
        if not self.exists_on_hub():
            print(f"📭 No vectorstore found on HF Hub")
            print(f"{'='*60}\n")
            return False
        
        try:
            # Download archive
            archive_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.CHROMA_ARCHIVE,
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
                force_download=True,  # Always get latest version
            )
            
            size_mb = os.path.getsize(archive_path) / (1024 * 1024)
            print(f"✅ Downloaded vectorstore from HF Hub ({size_mb:.2f} MB)")
            
            # Extract to local chroma_db/
            if self._extract_chroma_archive(archive_path):
                print(f"✅ Vectorstore ready at {self.CHROMA_DIR}")
                print(f"{'='*60}\n")
                return True
            else:
                print(f"{'='*60}\n")
                return False
            
        except Exception as e:
            print(f"❌ Failed to download vectorstore from HF Hub: {e}")
            print(f"{'='*60}\n")
            return False
    
    def clear_remote_vectorstore(self) -> bool:
        # Delete vectorstore archive from HF Hub
        #
        # Returns:
        #     True if successful, False otherwise
        
        print(f"\n{'='*60}")
        print(f"☁️ Clearing remote vectorstore from HF Hub...")
        
        try:
            # Delete the archive file
            self.api.delete_file(
                path_in_repo=self.CHROMA_ARCHIVE,
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
            )
            
            print(f"✅ Remote vectorstore cleared from HF Hub")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            # File might not exist, which is OK
            if "404" in str(e) or "Not Found" in str(e):
                print(f"✅ No remote vectorstore to clear (already empty)")
                print(f"{'='*60}\n")
                return True
            else:
                print(f"❌ Failed to clear remote vectorstore: {e}")
                print(f"{'='*60}\n")
                return False
    
    def sync_from_hub(self) -> bool:
        # Sync local vectorstore with HF Hub (download if exists)
        # Called on app startup
        #
        # Returns:
        #     True if sync successful or not needed, False on error
        
        if self.exists_on_hub():
            return self.download_vectorstore()
        else:
            print("📭 No remote vectorstore to sync")
            return True
    
    def sync_to_hub(self) -> bool:
        # Sync local vectorstore to HF Hub (upload)
        # Called after document indexing
        #
        # Returns:
        #     True if sync successful, False on error
        
        return self.upload_vectorstore()

