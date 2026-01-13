# app/services/tech_explanation_service.py
#
# Application service for the Tech Explanation use case.
#
# Responsibilities:
# - Orchestrate execution of the LCEL chain
# - Handle streaming and non-streaming use cases
# - Sanitize model output for UI consumption
# - Persist chat history permanently on Hugging Face Hub (append-only)
#
# This service contains NO prompt logic and NO UI logic.
# It is safe to reuse from UI, API, or background jobs.

from typing import Generator, List, Tuple
import json
from huggingface_hub import HfApi

from app.chains.tech_explanation_chain import tech_explanation_chain


class TechExplanationService:
    # --- HF Hub configuration ---
    HF_USERNAME = "gianmarioiamoni67"
    HF_REPO = "tech-explanation-service"
    HISTORY_FILE = "history.json"
    HF_TOKEN = None  # use Space token if available

    def __init__(self):
        self.api = HfApi()

    # -------------------------------------------------
    # LLM execution
    # -------------------------------------------------

    def explain_stream(self, topic: str) -> Generator[str, None, None]:
        accumulated = ""
        for chunk in tech_explanation_chain.stream({"topic": topic}):
            accumulated += chunk
            yield accumulated

    # -------------------------------------------------
    # History persistence (NO business logic)
    # -------------------------------------------------

    def load_history(self) -> List[Tuple[str, str]]:
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

    def save_history(self, history: List[Tuple[str, str]]) -> None:
        temp_file = "/tmp/history.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        self.api.upload_file(
            path_or_fileobj=temp_file,
            path_in_repo=self.HISTORY_FILE,
            repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
            repo_type="space",
            token=self.HF_TOKEN,
            commit_message="Update chat history",
        )
