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


class TechExplanationService:
    # --- Application service for generating technical explanations. ---
    #
    # This class intentionally contains no LangChain primitives such as
    # PromptTemplate or ChatOpenAI. All LLM logic is encapsulated in the LCEL chain.

    def explain(self, topic: str) -> str:
        # --- Generate a technical explanation for a given topic. ---
        #
        # Args:
        #     topic (str): The technical topic to explain.
        #
        # Returns:
        #     str: The generated explanation.
        

        # Input is passed as a dictionary, as required by LCEL invoke()
        result: Dict[str, Any] = tech_explanation_chain.invoke(
            {"topic": topic}
        )

        # By convention, LCEL chains return the final LLM output directly
        # or under a known key. Here we assume a string output.
        return result
    
    def tech_chain_stream(self, topic: str):
        # --- Stream output of LCEL chain ---
        #
        # Args:
        #     topic (str): The technical topic to explain.
        #
        # Returns:
        #     str: The generated explanation.
        # LCEL .stream() yields partial outputs
        return tech_explanation_chain.stream({"topic": topic})