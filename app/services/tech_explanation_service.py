# app/services/tech_explanation_service.py
#
# This module defines the TechExplanationService.
# It is responsible for orchestrating:
# - the prompt construction
# - the LLM invocation
# - returning the generated explanation
#
# The service is independent from the API layer and can be reused in
# notebooks, CLI scripts, or other programs.

from app.services.llm_factory import get_chat_llm
from app.prompts.tech_explanation_prompt import build_tech_explanation_prompt


class TechExplanationService:
    """
    Service layer to generate technical explanations for a given topic.

    Responsibilities:
    - Construct the structured prompt
    - Invoke the LLM chat model
    - Return the response content
    """

    def __init__(self):
        # Initialize the LLM and the prompt template
        self.llm = get_chat_llm()
        self.prompt = build_tech_explanation_prompt()

    def explain(self, topic: str) -> str:
        """
        Generate a technical explanation for the given topic.

        Args:
            topic (str): The topic to explain

        Returns:
            str: The model-generated technical explanation
        """

        # Format the messages with the user-supplied topic
        messages = self.prompt.format_messages(topic=topic)

        # Invoke the LLM chat model with the structured messages
        response = self.llm.invoke(messages)

        # Return the content of the AIMessage
        return response.content
