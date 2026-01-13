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
from langchain_core.runnables import RunnableParallel


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
        
        # Ordina le chat all'interno di ogni data per timestamp (newest first)
        for date_key in sorted_grouped:
            sorted_grouped[date_key] = sorted(
                sorted_grouped[date_key],
                key=lambda x: x["timestamp"],
                reverse=True
            )
        
        return sorted_grouped

    # -------------------------------
    # UI Helper Methods
    # -------------------------------
    @staticmethod
    def truncate(text: str, max_len: int) -> str:
        """Truncate text to max_len characters, adding '...' if needed"""
        return text[:max_len] + "..." if len(text) > max_len else text
    
    @staticmethod
    def parse_topic_from_selection(selection: str) -> Optional[str]:
        """
        Extract the topic from a dropdown selection.
        Returns None if it's a date header or invalid selection.
        """
        if not selection:
            return None
        
        # Ignore date headers (contain calendar emoji)
        if "📅" in selection:
            return None
        
        # Ignore special messages (no chats saved)
        if "📭" in selection:
            return None
        
        # Remove initial spaces (indentation from dropdown formatting)
        topic = selection.strip()
        
        # If empty after strip, it's not valid
        if not topic:
            return None
        
        return topic
    
    def create_history_choices(self, history, max_topic_len: int = 60) -> Tuple[List[str], Optional[str]]:
        """
        Create formatted choices for the history dropdown, grouped by date.
        Returns (choices_list, default_value).
        """
        if not history:
            return ["📭 No chats saved"], None
        
        # Group by date
        grouped = self.group_by_date(history)
        
        choices = []
        
        for date_key, chats in grouped.items():
            date_label = chats[0]["date_label"]
            
            # Date header with calendar emoji as identifier
            date_header = f"📅 {date_label}"
            choices.append(date_header)
            
            # Chat items under the date - indented with 2 spaces
            for chat in chats:
                topic_display = self.truncate(chat["topic"], max_topic_len)
                choices.append(f"  {topic_display}")
        
        return choices, None
    
    def create_delete_choices(self, history, max_topic_len: int = 50) -> List[str]:
        """Create formatted choices for the delete dropdown with numeric IDs"""
        return [f"{i}. {self.truncate(h[0], max_topic_len)}" for i, h in enumerate(history)] if history else []
    
    # -------------------------------
    # Multi-topic parsing
    # -------------------------------
    def parse_topics(self, raw_input: str) -> List[str]:
        # Split comma-separated topics and clean them
        topics = [t.strip() for t in raw_input.split(",")]
        return [t for t in topics if t]

    # -------------------------------
    # Multi-topic streaming (sequential UX)
    # -------------------------------
    def explain_multiple_stream(
        self, raw_topics: str
    ) -> Generator[Tuple[str, str], None, None]:
        # Streams explanations for multiple topics sequentially.
        # Yields (topic, accumulated_text).
        topics = self.parse_topics(raw_topics)

        for topic in topics:
            accumulated = ""
            for chunk in tech_explanation_chain.stream({"topic": topic}):
                accumulated += chunk
                yield topic, accumulated
    
    # -------------------------------
    # History Loading and Aggregation
    # -------------------------------
    def find_chat_by_topic(self, topic_display: str, history) -> Optional[Tuple[str, str]]:
        """
        Find a chat in history by topic (supports truncated topics ending with '...').
        Returns (topic, explanation) if found, None otherwise.
        """
        is_truncated = topic_display.endswith("...")
        
        for item in history:
            topic = item[0]
            explanation = item[1]
            
            if is_truncated:
                # Match by prefix (without the '...')
                topic_prefix = topic_display[:-3]
                if topic.startswith(topic_prefix):
                    return topic, explanation
            else:
                # Exact match
                if topic == topic_display:
                    return topic, explanation
        
        # Try case-insensitive match as fallback
        topic_lower = topic_display.lower().replace("...", "")
        for item in history:
            topic = item[0]
            if topic.lower().startswith(topic_lower):
                return topic, item[1]
        
        return None
    
    def get_chats_by_date(self, date_str: str, history) -> Optional[List[dict]]:
        """
        Get all chats for a specific date.
        date_str format: "DD/MM/YYYY"
        Returns list of chat dicts or None if not found.
        """
        grouped = self.group_by_date(history)
        
        for date_key, chats in grouped.items():
            if chats[0]["date_label"] == date_str:
                return chats
        
        return None
    
    def format_chats_for_date(self, date_str: str, chats: List[dict]) -> Tuple[str, str]:
        """
        Format multiple chats for display when a date is selected.
        Returns (combined_topic, combined_output).
        """
        combined_output = f"📅 Chat del {date_str}\n"
        combined_output += "=" * 60 + "\n\n"
        
        for i, chat in enumerate(chats, 1):
            combined_output += f"🔹 Chat {i}: {chat['topic']}\n"
            combined_output += "─" * 60 + "\n"
            combined_output += chat['explanation'] + "\n\n"
            if i < len(chats):
                combined_output += "\n"
        
        combined_topic = f"📅 {date_str} ({len(chats)} chat)"
        return combined_topic, combined_output
    
    def aggregate_topics_output(self, topics: List[str], topic_contents: dict) -> str:
        """
        Aggregate multiple topics into a single output with separators.
        Used for aggregate mode in streaming.
        """
        accumulated = ""
        for t in topics:
            if t in topic_contents:
                if accumulated:  # Add separator between topics
                    accumulated += f"\n\n{'='*60}\n\n"
                accumulated += f"{t}:\n\n{topic_contents[t]}"
        return accumulated

