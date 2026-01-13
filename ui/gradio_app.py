import gradio as gr
from app.services.tech_explanation_service import TechExplanationService

# -------------------------------
# Inizializzazione servizio
# -------------------------------
service = TechExplanationService()
loaded_history = service.load_history()

# -------------------------------
# Callback streaming
# -------------------------------
def explain_topic_stream(topic: str, history):
    topic_clean = (topic or "").strip()
    if not topic_clean:
        yield history, "Please enter a technical topic.", gr.update()
        return

    # Accumula i chunk RAW dallo streaming
    accumulated_raw = ""
    for chunk in service.explain_stream(topic_clean):
        accumulated_raw = chunk
        yield history, accumulated_raw, gr.update()

    # Sanitizzazione finale con paragrafi
    final_text = service._sanitize_output(accumulated_raw)

    # Aggiorna history e salva su HF (con error handling integrato)
    new_history = service.add_to_history(topic_clean, final_text, history)

    # Aggiorna dropdown
    topics = [t for t, _ in new_history]
    yield new_history, final_text, gr.update(choices=topics, value=topic_clean)


# -------------------------------
# Callback chat precedente
# -------------------------------
def load_previous_chat(selected_topic, history):
    for t, e in history:
        if t == selected_topic:
            return t, e
    return "", ""


# -------------------------------
# UI
# -------------------------------
with gr.Blocks(title="Tech Explanation Service") as demo:
    gr.Markdown(
        "# Tech Explanation Service\nInserisci un topic tecnico e ricevi una spiegazione chiara e strutturata."
    )

    history_state = gr.State(loaded_history)

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
                with gr.Column(scale=0, min_width=150):
                    explain_button = gr.Button(
                        "Explain",
                        variant="primary",
                    )

        with gr.Column(scale=1):
            history_dropdown = gr.Dropdown(
                label="Previous chats",
                choices=[t for t, _ in loaded_history],
                interactive=True,
            )

    # -------------------------------
    # Eventi
    # -------------------------------
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

if __name__ == "__main__":
    demo.launch()
