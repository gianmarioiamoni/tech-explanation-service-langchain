# app/services/tech_explanation_service.py
#
# Service for technical explanations with persistent history on HF Hub
# Handle streaming, sanitization of output and reading/saving history.

from typing import Generator
import re
import json
import os
from huggingface_hub import HfApi, hf_hub_download
from app.chains.tech_explanation_chain import tech_explanation_chain

class TechExplanationService:
    HF_USERNAME = "gianmarioiamoni67"
    HF_REPO = "tech-explanation-service"
    HISTORY_FILE = "history.json"
    HF_TOKEN = None  # usa token dello space se necessario

    def __init__(self):
        self.api = HfApi()
        self._verify_hf_setup()

    # -------------------------------
    # Sanitizzazione output
    # -------------------------------
    def _sanitize_output(self, text: str) -> str:
        """Rimuove Markdown e formatting indesiderato, preserva emoji e simboli"""
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)

        # aggiunge un '\n\n' tra frasi (assumendo che ogni frase termini con punto)
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        return "\n\n".join([s + "." for s in sentences])

    # -------------------------------
    # Streaming spiegazioni
    # -------------------------------
    def explain_stream(self, topic: str) -> Generator[str, None, None]:
        """Genera l'output dell'LLM chunk per chunk (non va a capo ogni parola)"""
        accumulated = ""
        for chunk in tech_explanation_chain.stream({"topic": topic}):
            accumulated += chunk
            # yield il testo accumulato RAW (senza sanitizzazione finale)
            yield accumulated

    # -------------------------------
    # Verifica setup HF Hub
    # -------------------------------
    def _verify_hf_setup(self):
        """Verifica se HF Hub è accessibile e crea il file history se manca"""
        try:
            # Prova a caricare la history esistente
            self.load_history()
            print("✅ HF Hub configurato correttamente")
        except Exception as e:
            print(f"⚠️ HF Hub setup issue: {e}")
            print("💡 La history sarà disponibile solo nella sessione corrente")
            print("   Per persistenza su HF Hub:")
            print("   1. Assicurati che il repo Space esista su HF")
            print("   2. Configura HF_TOKEN se necessario")

    # -------------------------------
    # Gestione History HF Hub
    # -------------------------------
    def load_history(self):
        """Carica la history da HF Hub. Ritorna lista vuota se non esiste."""
        try:
            file_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.HISTORY_FILE,
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
            )
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                print(f"📚 History caricata da HF Hub ({len(history)} items)")
                return history
        except Exception as e:
            print(f"⚠️ Impossibile caricare history da HF Hub: {e}")
            print("   Inizializzazione con history vuota")
            return []

    def save_history(self, history):
        """Salva la history su HF Hub. Ritorna True se successo, False altrimenti."""
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
    
    def add_to_history(self, topic: str, explanation: str, history):
        """Aggiunge una nuova interazione e persiste su HF Hub"""
        new_history = history + [(topic, explanation)]
        success = self.save_history(new_history)
        if not success:
            print("⚠️ History non salvata su HF Hub, ma disponibile nella sessione")
        return new_history
