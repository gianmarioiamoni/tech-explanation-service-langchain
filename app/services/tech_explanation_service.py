# app/services/tech_explanation_service.py
#
# This service acts as a thin application-layer wrapper around the LCEL chain.
# Its responsibility is orchestration, not prompt engineering or LLM logic.
#
# - It exposes a stable API for UI and HTTP layers
# - It delegates execution to a pure LCEL chain
# - It can easily support invoke(), stream(), or batch() in the future


from typing import Dict, Any, Generator
import re
import json
from huggingface_hub import HfApi

from app.chains.tech_explanation_chain import tech_explanation_chain

class TechExplanationService:
    # --- HF Hub configuration ---
    HF_USERNAME = "gianmarioiamoni67"
    HF_REPO = "tech-explanation-service"
    HISTORY_FILE = "history.json"
    HF_TOKEN = None  # if needed, else relies on space token

    def __init__(self):
        """Initialize the service with HF Hub API client"""
        self.api = HfApi()

    # --- Internal helper methods ---

    def _sanitize_output(self, text: str) -> str:
        # Clean text output for UI
        #
        # This method:
        # - Removes Markdown headers (#, ##)
        # - Strips bold/italic formatting while preserving emoji and symbols
        # - Leaves emoji like 🔴, 🟠, 🟢 intact
        # - Strips extra whitespace
        #
   

        # Remove Markdown headers (e.g., # Heading)
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE).strip()

        # Remove bold (**text**) or italic (*text*) but keep inner content
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text).strip()
        text = re.sub(r"\*(.*?)\*", r"\1", text).strip()

        # Remove inline code ticks (`text`)
        text = re.sub(r"`(.*?)`", r"\1", text).strip()

        # Remove excessive leading/trailing whitespace
        return text.strip()



    def explain(self, topic: str) -> str:
        # Generate a full (non-streaming) technical explanation.
        # Args:
        #     topic (str): The technical topic to explain.
        # Returns:
        #     str: The sanitized explanation text.
        result = tech_explanation_chain.invoke({"topic": topic})

        # The chain is expected to return a string output
        return self._sanitize_output(result)

    def explain_stream(self, topic: str) -> Generator[str, None, None]:
        # Stream a technical explanation incrementally.
        # Args:
        #     topic (str): The technical topic to explain.
        # Yields:
        #     str: The progressively accumulated explanation
        accumulated = ""

        # LCEL .stream() yields partial chunks of model output
        for chunk in tech_explanation_chain.stream({"topic": topic}):
            # Don't sanitize during streaming - just accumulate raw chunks
            accumulated += chunk
            yield accumulated

    
    def load_history(self):
        """Load chat history from HF Hub JSON file"""
        try:
            file_path = self.api.download_file(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.HISTORY_FILE,
                repo_type="space",
                token=self.HF_TOKEN,
            )
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_history(self, history):
        """Save chat history to HF Hub JSON file"""
        temp_file = "/tmp/history.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        self.api.upload_file(
            path_or_fileobj=temp_file,
            path_in_repo=self.HISTORY_FILE,
            repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
            repo_type="space",
            token=self.HF_TOKEN,
            commit_message="Update chat history"
        )

    def add_to_history(self, topic: str, explanation: str, history):
        """Append new interaction and persist"""
        history = history + [(topic, explanation)]
        self.save_history(history)
        return history


    