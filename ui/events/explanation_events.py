# ui/events/explanation_events.py
#
# Explanation generation events
#
# Responsibilities:
# - Wire explain button click event
# - Wire topic input submit event
# - Wire stop button event
# - Manage streaming and button states

import gradio as gr
from ui.callbacks import explain_topic_stream


def wire_explanation_events(explain_btn, topic_input, stop_btn, download_btn, clear_btn,
                            history_state, history_mode, rag_uploaded_state, output_box,
                            history_dropdown, delete_dropdown, download_accordion, download_file):
    # Wire all explanation-related events with streaming support
    #
    # Args:
    #     explain_btn: gr.Button for triggering explanation
    #     topic_input: gr.Textbox for topic input
    #     stop_btn: gr.Button for stopping generation
    #     download_btn: gr.Button for downloading chat
    #     clear_btn: gr.Button for clearing output
    #     history_state: gr.State for chat history
    #     history_mode: gr.Radio for multi-topic behavior
    #     rag_uploaded_state: gr.State for RAG documents
    #     output_box: gr.Textbox for output display
    #     history_dropdown: gr.Dropdown for history selection
    #     delete_dropdown: gr.Dropdown for delete selection
    #     download_accordion: gr.Accordion for download format selection
    #     download_file: gr.File for file download
    
    # -------------------------------
    # Explain button click
    # -------------------------------
    click_enable = explain_btn.click(
        fn=lambda: gr.update(interactive=True),
        inputs=None,
        outputs=[stop_btn],
    )
    
    click_stream = click_enable.then(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state, history_mode, rag_uploaded_state],
        outputs=[history_state, output_box, history_dropdown, delete_dropdown],
    )
    
    click_disable = click_stream.then(
        fn=lambda: (gr.update(interactive=False), gr.update(interactive=True)),
        inputs=None,
        outputs=[stop_btn, download_btn],
    )
    
    # -------------------------------
    # Topic input submit (Enter key)
    # -------------------------------
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
    
    # -------------------------------
    # Stop button
    # -------------------------------
    stop_click = stop_btn.click(
        fn=lambda: gr.update(interactive=False),
        inputs=None,
        outputs=[stop_btn],
        cancels=[click_stream, submit_stream],
    )
    
    stop_click.then(
        fn=lambda: gr.update(interactive=True),
        inputs=None,
        outputs=[download_btn],
    )
    
    # -------------------------------
    # Clear button
    # -------------------------------
    clear_btn.click(
        fn=lambda: ("", "", gr.update(interactive=False), gr.update(visible=False, open=True), gr.update(visible=False, value=None)),
        inputs=None,
        outputs=[topic_input, output_box, download_btn, download_accordion, download_file],
    )

