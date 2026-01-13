# app/services/tech_explanation_service.py
#
# Service for technical explanations with persistent history on HF Hub
# Handle streaming, sanitization of output and reading/saving history.

from typing import Generator, List, Tuple, Optional
import re
import json
import os
from datetime import datetime
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
        """Rimuove solo il Markdown, mantenendo la struttura naturale del testo"""
        # Rimuove code blocks PRIMA (```...```) per evitare conflitti con inline code
        # Usa re.DOTALL per matchare anche i newline
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        
        # Rimuove Markdown headers (###)
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        
        # Rimuove bold (**text**)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        
        # Rimuove italic (*text*)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        
        # Rimuove inline code (`text`)
        text = re.sub(r"`(.*?)`", r"\1", text)
        
        # Pulisci spazi multipli
        text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 newline consecutive
        text = re.sub(r" {2,}", " ", text)  # Max 1 spazio tra parole
        
        return text.strip()

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
            # Force download from server, not cache
            file_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.HISTORY_FILE,
                repo_type="space",
                token=self.HF_TOKEN or os.getenv("HF_TOKEN"),
                force_download=True,  # Bypassa la cache locale
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
        """Aggiunge una nuova interazione con timestamp e persiste su HF Hub"""
        timestamp = datetime.now().isoformat()
        # Supporta sia vecchio formato (topic, explanation) che nuovo (topic, explanation, timestamp)
        new_entry = (topic, explanation, timestamp)
        new_history = history + [new_entry]
        success = self.save_history(new_history)
        if not success:
            print("⚠️ History non salvata su HF Hub, ma disponibile nella sessione")
        return new_history
    
    def delete_from_history(self, index: int, history) -> List:
        """Rimuove una chat dall'history per indice"""
        if 0 <= index < len(history):
            new_history = history[:index] + history[index+1:]
            self.save_history(new_history)
            print(f"🗑️ Chat {index} rimossa dall'history")
            return new_history
        print(f"⚠️ Indice {index} non valido")
        return history
    
    def search_history(self, query: str, history) -> List[Tuple]:
        """Cerca nelle chat per query (case-insensitive)"""
        if not query.strip():
            return history
        
        query_lower = query.strip().lower()
        results = []
        for item in history:
            topic = item[0]
            explanation = item[1]
            # Cerca in topic o explanation
            if query_lower in topic.lower() or query_lower in explanation.lower():
                results.append(item)
        
        print(f"🔍 Trovate {len(results)} chat per query '{query}'")
        return results
    
    def group_by_date(self, history) -> dict:
        """Raggruppa le chat per giorno"""
        from collections import defaultdict
        
        grouped = defaultdict(list)
        for item in history:
            # Supporta sia vecchio formato (2 elementi) che nuovo (3 elementi)
            if len(item) == 3:
                topic, explanation, timestamp = item
            else:
                # Vecchio formato senza timestamp
                topic, explanation = item
                timestamp = datetime.now().isoformat()
            
            # Estrai la data (senza ora)
            try:
                dt = datetime.fromisoformat(timestamp)
                date_key = dt.strftime("%Y-%m-%d")
                date_label = dt.strftime("%d/%m/%Y")
            except:
                date_key = "unknown"
                date_label = "Data sconosciuta"
            
            grouped[date_key].append({
                "topic": topic,
                "explanation": explanation,
                "timestamp": timestamp,
                "date_label": date_label
            })
        
        # Ordina per data (più recente prima)
        sorted_grouped = dict(sorted(grouped.items(), reverse=True))
        return sorted_grouped
