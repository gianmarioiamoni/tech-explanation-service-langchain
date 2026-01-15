# ui/gradio_app.py
#
# Gradio UI for the Tech Explanation Service
#
# Responsibilities:
# - Define the Gradio UI layout and components
# - Wire up event handlers to callbacks
# - Launch the Gradio application
#
# Note: Business logic and callbacks are in separate modules:
# - app/services/tech_explanation_service.py (business logic)
# - ui/callbacks/ (Gradio event callbacks)
# - ui/utils/ (UI utilities and constants)

import sys
from pathlib import Path

# Add project root to path to allow import of 'app'
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gradio as gr

# Import callbacks
from ui.callbacks import (
    explain_topic_stream,
    initialize_history,
    load_selected_chat,
    delete_selected_chat,
    search_in_history,
)
from ui.callbacks.download_callbacks import download_chat
from ui.callbacks.upload_callbacks import upload_documents, clear_rag_index  # NEW RAG callbacks

# -------------------------------
# UI Layout and Components
# -------------------------------
with gr.Blocks(title="Tech Explanation Service") as demo:
    gr.Markdown(
        "# 🎓 Tech Explanation Service\nEnter one or more technical topics (separated by commas) \nand receive a clear and structured explanation."
    )

    # State
    history_state = gr.State([])
    rag_uploaded_state = gr.State([])  # Track uploaded RAG documents

    with gr.Row():
        with gr.Column(scale=2):
            # -------------------------------
            # RAG Document Upload (Collapsible)
            # -------------------------------
            with gr.Accordion("📚 Upload Documents for Context-Aware Answers (RAG)", open=False):
                rag_file_upload = gr.File(
                    label="📂 Select Files",
                    file_types=[".pdf", ".txt", ".docx"],
                    file_count="multiple",
                    type="filepath",
                )
                with gr.Row():
                    rag_clear_btn = gr.Button(
                        "🗑️ Clear All Documents",
                        variant="secondary",
                        scale=1,
                    )

            # Status always visible
            rag_status_box = gr.Textbox(
                label="📄 Uploaded Documents Status",
                lines=2,
                interactive=False,
                value="No documents uploaded.",
            )

            # -------------------------------
            # Topic input and options
            # -------------------------------
            topic_input = gr.Textbox(
                label="📝 Technical Topic",
                placeholder="e.g., Python decorators, Docker networking, RAG architecture",
                lines=1,
            )

            history_mode = gr.Radio(
                label="Multi-topic behavior",
                choices=[
                    "Aggregate into one chat",
                    "Save each topic as a separate chat"
                ],
                value="Aggregate into one chat",
            )

            output_box = gr.Textbox(
                label="💡 Explanation",
                lines=18,
                interactive=False,
                autoscroll=True,
            )

            # -------------------------------
            # Buttons row
            # -------------------------------
            with gr.Row():
                explain_button = gr.Button(
                    "✨ Explain",
                    variant="primary",
                    scale=2,
                )
                stop_btn = gr.Button(
                    "⏹️ Stop",
                    variant="stop",
                    scale=1,
                    interactive=False,
                )
                download_btn = gr.Button(
                    "📥 Download",
                    variant="huggingface",
                    scale=1,
                    interactive=False,
                )
                clear_button = gr.Button(
                    "🔄 Clear",
                    variant="secondary",
                    scale=1,
                )

            # -------------------------------
            # Download submenu
            # -------------------------------
            with gr.Accordion("📥 Select Format", open=True, visible=False) as download_accordion:
                with gr.Row():
                    download_md_btn = gr.Button(
                        "📄 Markdown",
                        variant="secondary",
                        scale=1,
                    )
                    download_pdf_btn = gr.Button(
                        "📕 PDF",
                        variant="secondary",
                        scale=1,
                    )
                    download_docx_btn = gr.Button(
                        "📘 Word",
                        variant="secondary",
                        scale=1,
                    )

            download_file = gr.File(
                label="📥 Download File",
                visible=False,
                interactive=False,
            )

        # -------------------------------
        # Chat History Column
        # -------------------------------
        with gr.Column(scale=1):
            gr.Markdown("### 📚 Chat History")

            search_box = gr.Textbox(
                label="🔍 Search",
                placeholder="Search in chats...",
                lines=1,
            )

            history_dropdown = gr.Dropdown(
                label="📚 Previous chats (newest first)",
                choices=["⏳ Loading..."],
                value=None,
                interactive=True,
                allow_custom_value=False,
            )

            gr.Markdown("---")

            with gr.Accordion("🗑️ Delete Chat", open=False):
                delete_dropdown = gr.Dropdown(
                    label="Select chat to delete",
                    choices=[],
                    value=None,
                    interactive=True,
                )
                delete_button = gr.Button(
                    "🗑️ Delete Selected",
                    variant="stop",
                )

    # -------------------------------
    # Events
    # -------------------------------

    # Initialization
    demo.load(
        fn=initialize_history,
        inputs=None,
        outputs=[history_state, history_dropdown, delete_dropdown, search_box],
    )

    # Search
    search_box.change(
        fn=search_in_history,
        inputs=[search_box, history_state],
        outputs=[history_dropdown],
    )

    # Selection of chat
    history_dropdown.change(
        fn=load_selected_chat,
        inputs=[history_dropdown, history_state],
        outputs=[topic_input, output_box],
    ).then(
        fn=lambda text: gr.update(interactive=bool(text)),
        inputs=[output_box],
        outputs=[download_btn],
    )

    # -------------------------------
    # Upload callbacks
    # -------------------------------
    rag_file_upload.upload(
        fn=upload_documents,
        inputs=[rag_file_upload, rag_uploaded_state],
        outputs=[rag_uploaded_state, rag_status_box],
    )

    rag_clear_btn.click(
        fn=clear_rag_index,
        inputs=[rag_uploaded_state],
        outputs=[rag_uploaded_state, rag_status_box],
    )

    # -------------------------------
    # Explain callbacks
    # -------------------------------
    click_enable = explain_button.click(
        fn=lambda: gr.update(interactive=True),
        inputs=None,
        outputs=[stop_btn],
    )

    click_stream = click_enable.then(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state, history_mode, rag_uploaded_state],  # Pass uploaded docs to callback
        outputs=[history_state, output_box, history_dropdown, delete_dropdown],
    )

    click_disable = click_stream.then(
        fn=lambda: (gr.update(interactive=False), gr.update(interactive=True)),
        inputs=None,
        outputs=[stop_btn, download_btn],
    )

    submit_enable = topic_input.submit(
        fn=lambda: gr.update(interactive=True),
        inputs=None,
        outputs=[stop_btn],
    )

    submit_stream = submit_enable.then(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state, history_mode, rag_uploaded_state],
        outputs=[history_state, output_box, history_dropdown, delete_dropdown],
    )

    submit_disable = submit_stream.then(
        fn=lambda: (gr.update(interactive=False), gr.update(interactive=True)),
        inputs=None,
        outputs=[stop_btn, download_btn],
    )

    # Stop button
    stop_btn.click(
        fn=lambda: gr.update(interactive=False),
        inputs=None,
        outputs=[stop_btn],
        cancels=[click_stream, submit_stream],
    )

    # -------------------------------
    # Download buttons
    # -------------------------------
    download_btn.click(
        fn=lambda: (gr.update(visible=True, open=True), gr.update(visible=False, value=None)),
        inputs=None,
        outputs=[download_accordion, download_file],
    )

    download_md_btn.click(
        fn=lambda topic, output: download_chat(topic, output, "Markdown"),
        inputs=[topic_input, output_box],
        outputs=[download_file],
    ).then(
        fn=lambda file: (gr.update(visible=bool(file)), gr.update(visible=False, open=True)),
        inputs=[download_file],
        outputs=[download_file, download_accordion],
    )

    download_pdf_btn.click(
        fn=lambda topic, output: download_chat(topic, output, "PDF"),
        inputs=[topic_input, output_box],
        outputs=[download_file],
    ).then(
        fn=lambda file: (gr.update(visible=bool(file)), gr.update(visible=False, open=True)),
        inputs=[download_file],
        outputs=[download_file, download_accordion],
    )

    download_docx_btn.click(
        fn=lambda topic, output: download_chat(topic, output, "Word"),
        inputs=[topic_input, output_box],
        outputs=[download_file],
    ).then(
        fn=lambda file: (gr.update(visible=bool(file)), gr.update(visible=False, open=True)),
        inputs=[download_file],
        outputs=[download_file, download_accordion],
    )

    # Clear button
    clear_button.click(
        fn=lambda: ("", "", gr.update(interactive=False), gr.update(visible=False, open=True), gr.update(visible=False, value=None)),
        inputs=None,
        outputs=[topic_input, output_box, download_btn, download_accordion, download_file],
    )

    # Delete button
    delete_button.click(
        fn=delete_selected_chat,
        inputs=[delete_dropdown, history_state, search_box],
        outputs=[history_state, history_dropdown, delete_dropdown, topic_input, output_box],
    )

# Enable queue for streaming
demo.queue()

if __name__ == "__main__":
    demo.launch()

