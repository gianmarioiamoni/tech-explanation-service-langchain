# ui/gradio_app.py
#
# This module defines the Gradio user interface for the Tech Explanation Service.
# The UI acts as a thin presentation layer that delegates all business logic
# to the TechExplanationService.
#
# Responsibilities:
# - Collect user input (technical topic)
# - Call the service layer
# - Display the generated explanation
#
# No prompt or LLM logic should be implemented here.

import sys
from pathlib import Path

# Add project root to Python path to enable imports from 'app' package
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gradio as gr
from app.services.tech_explanation_service import TechExplanationService


# Initialize the service once
service = TechExplanationService()


def explain_topic(topic: str) -> str:
    """
    Gradio callback function.

    Args:
        topic (str): The technical topic provided by the user

    Returns:
        str: AI-generated technical explanation
    """
    if not topic or not topic.strip():
        return "Please provide a valid technical topic."

    return service.explain(topic.strip())


# --- Gradio UI definition ---
with gr.Blocks(title="Tech Explanation Service") as demo:
    gr.Markdown(
        """
        # Tech Explanation Service
        Generate clear and structured technical explanations using
        few-shot prompting and LangChain.
        """
    )

    topic_input = gr.Textbox(
        label="Technical Topic",
        placeholder="e.g. Few-Shot Prompting in LangChain",
        lines=1,
    )

    explanation_output = gr.Textbox(
        label="AI Explanation",
        lines=10,
    )

    # Button placed in a row to keep natural width
    with gr.Row():
        with gr.Column(scale=0):
            explain_button = gr.Button("Explain")

    # Trigger explanation on button click
    explain_button.click(
        fn=explain_topic,
        inputs=topic_input,
        outputs=explanation_output,
    )

    # Trigger explanation when pressing Enter in the textbox
    topic_input.submit(
        fn=explain_topic,
        inputs=topic_input,
        outputs=explanation_output,
    )


if __name__ == "__main__":
    demo.launch()