# app/ui/gradio_app.py
#
# Gradio UI for the Tech Explanation Service
# Streaming + History + Dropdown (correct Gradio update handling)

import gradio as gr
from app.services.tech_explanation_service import TechExplanationService

# ------------------------------------------------------------------
# Service initialization
# ------------------------------------------------------------------
service = TechExplanationService()

# ------------------------------------------------------------------
# Streaming callback with history
# ------------------------------------------------------------------
def explain_topic_stream(topic: str, history):
    topic_clean = (topic or "").strip()
    if not topic_clean:
        yield history, "Please enter a technical topic.", gr.update()
        return

    accumulated = ""

    for chunk in service.explain_stream(topic_clean):
        accumulated = chunk
        yield history, accumulated, gr.update()

    # Persist history
    history = service.add_to_history(topic_clean, accumulated, history)

    # Update dropdown choices safely
    topics = [t for t, _ in history]

    yield (
        history,
        accumulated,
        gr.update(choices=topics, value=topic_clean),
    )

# ------------------------------------------------------------------
# Load previous chat
# ------------------------------------------------------------------
def load_previous_chat(selected_topic, history):
    for t, e in history:
        if t == selected_topic:
            return t, e
    return "", ""

# ------------------------------------------------------------------
# UI definition
# ------------------------------------------------------------------
with gr.Blocks(title="Tech Explanation Service") as demo:
    gr.Markdown(
        """
        # Tech Explanation Service

        Enter a technical topic and receive a clear explanation.
        """
    )

    history_state = gr.State(service.load_history())

    with gr.Row():
        with gr.Column(scale=2):
            topic_input = gr.Textbox(
                label="Technical topic",
                placeholder="e.g. Python, Docker, RAG",
                lines=1,
            )

            output_box = gr.Textbox(
                label="Explanation",
                lines=15,
                interactive=False,
            )

            with gr.Row():
                with gr.Column(scale=0):
                    explain_button = gr.Button("Explain")

        with gr.Column(scale=1):
            history_dropdown = gr.Dropdown(
                label="Previous chats",
                choices=[t for t, _ in service.load_history()],
                interactive=True,
            )

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    history_dropdown.change(
        fn=load_previous_chat,
        inputs=[history_dropdown, history_state],
        outputs=[topic_input, output_box],
    )

    explain_button.click(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state],
        outputs=[history_state, output_box, history_dropdown],
    )

    topic_input.submit(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state],
        outputs=[history_state, output_box, history_dropdown],
    )
