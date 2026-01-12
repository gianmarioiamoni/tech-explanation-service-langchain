# app/services/tech_explanation_service.py
#
# This service acts as a thin application-layer wrapper around the LCEL chain.
# Its responsibility is orchestration, not prompt engineering or LLM logic.
#
# - It exposes a stable API for UI and HTTP layers
# - It delegates execution to a pure LCEL chain
# - It can easily support invoke(), stream(), or batch() in the future


from typing import Dict, Any

from app.chains.tech_explanation_chain import tech_explanation_chain


# app/services/tech_explanation_service.py
#
# Application service for generating technical explanations.
#
# This service acts as the boundary between the UI/API layers and the LCEL chain.
# It is responsible for:
# - Invoking the LCEL chain
# - Handling streaming vs non-streaming execution
# - Adapting and sanitizing outputs for UI consumption

from typing import Generator
from app.chains.tech_explanation_chain import tech_explanation_chain

import re

class TechExplanationService:
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
        #     str: The progressively accumulated, sanitized explanation
        accumulated = ""

        # LCEL .stream() yields partial chunks of model output
        for chunk in tech_explanation_chain.stream({"topic": topic}):
            accumulated += self._sanitize_output(chunk)
            yield accumulated
