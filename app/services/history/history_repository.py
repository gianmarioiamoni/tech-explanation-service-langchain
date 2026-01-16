# app/services/history/history_repository.py
#
# Repository for chat history persistence on Hugging Face Hub
#
# Responsibilities:
# - Load history from HF Hub
# - Save history to HF Hub
# - Add new chat to history
# - Delete chat from history
# - Verify HF Hub setup

import json
import os
from datetime import datetime
from typing import List, Tuple
from huggingface_hub import HfApi, hf_hub_download


class HistoryRepository:
    """Repository for managing chat history persistence on Hugging Face Hub"""
    
    # Configuration constants
    HF_USERNAME = "gianmarioiamoni67"
    HF_REPO = "tech-explanation-service"
    HISTORY_FILE = "history.json"
    HF_TOKEN = None  # Uses space token if needed
    
    def __init__(self):
        self.api = HfApi()
        self._verify_hf_setup()
    
    def _verify_hf_setup(self):
        """Verify if HF Hub is accessible and create history file if missing"""
        try:
            # Try to load existing history
            self.load_history()
            print("✅ HF Hub configurato correttamente")
        except Exception as e:
            print(f"⚠️ HF Hub setup issue: {e}")
            print("💡 La history sarà disponibile solo nella sessione corrente")
            print("   Per persistenza su HF Hub:")
            print("   1. Assicurati che il repo Space esista su HF")
            print("   2. Configura HF_TOKEN se necessario")
    
    def load_history(self) -> List:
        """
        Load history from HF Hub.
        Returns empty list if history doesn't exist.
        
        Returns:
            List of chat history entries (topic, explanation, timestamp)
        """
        try:
            # Force download from server, not cache
            file_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.HISTORY_FILE,
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
                force_download=True,  # Bypass local cache
            )
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                print(f"📚 History caricata da HF Hub ({len(history)} items)")
                return history
        except Exception as e:
            print(f"⚠️ Impossibile caricare history da HF Hub: {e}")
            print("   Inizializzazione con history vuota")
            return []
    
    def save_history(self, history: List) -> bool:
        """
        Save history to HF Hub.
        
        Args:
            history: List of chat entries to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            temp_file = "/tmp/history.json"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            self.api.upload_file(
                path_or_fileobj=temp_file,
                path_in_repo=self.HISTORY_FILE,
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
                commit_message="Aggiornamento storico chat",
            )
            print(f"✅ History salvata su HF Hub ({len(history)} items)")
            return True
        except Exception as e:
            print(f"❌ Errore salvataggio su HF Hub: {e}")
            print("   💡 Possibili cause:")
            print("      - Token HF non configurato")
            print("      - Repo Space non esiste o non hai permessi")
            print("      - history.json non esiste nel repo")
            return False
    
    def add_to_history(self, topic: str, explanation: str, history: List) -> List:
        """
        Add a new chat to history with timestamp and persist to HF Hub.
        
        Args:
            topic: Topic of the chat
            explanation: Explanation text
            history: Current history list
            
        Returns:
            Updated history list
        """
        timestamp = datetime.now().isoformat()
        # Support both old format (topic, explanation) and new (topic, explanation, timestamp)
        new_entry = (topic, explanation, timestamp)
        new_history = history + [new_entry]
        success = self.save_history(new_history)
        if not success:
            print("⚠️ History non salvata su HF Hub, ma disponibile nella sessione")
        return new_history
    
    def delete_from_history(self, index: int, history: List) -> List:
        """
        Remove a chat from history by index.
        
        Args:
            index: Index of chat to delete
            history: Current history list
            
        Returns:
            Updated history list
        """
        if 0 <= index < len(history):
            new_history = history[:index] + history[index+1:]
            self.save_history(new_history)
            print(f"🗑️ Chat {index} rimossa dall'history")
            return new_history
        print(f"⚠️ Indice {index} non valido")
        return history

