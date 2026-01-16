# ui/events/download_events.py
#
# Download/export events
#
# Responsibilities:
# - Wire download button event (show format selection)
# - Wire format selection buttons (MD, PDF, DOCX)

import gradio as gr
from ui.callbacks.download_callbacks import download_chat


def wire_download_events(download_btn, download_accordion, download_md_btn, download_pdf_btn,
                         download_docx_btn, download_file, topic_input, output_box):
    # Wire all download-related events
    #
    # Args:
    #     download_btn: gr.Button for initiating download
    #     download_accordion: gr.Accordion for format selection
    #     download_md_btn: gr.Button for Markdown format
    #     download_pdf_btn: gr.Button for PDF format
    #     download_docx_btn: gr.Button for Word format
    #     download_file: gr.File for file download
    #     topic_input: gr.Textbox for topic (needed for filename)
    #     output_box: gr.Textbox for content to download
    
    # -------------------------------
    # Download button - show format selection
    # -------------------------------
    download_btn.click(
        fn=lambda: gr.update(visible=True, open=True),
        inputs=None,
        outputs=[download_accordion],
    )
    
    # -------------------------------
    # Markdown format
    # -------------------------------
    download_md_btn.click(
        fn=download_chat,
        inputs=[topic_input, output_box, gr.State("Markdown")],
        outputs=[download_file],
    ).then(
        fn=lambda: (gr.update(visible=False, open=False), gr.update(visible=True)),
        inputs=None,
        outputs=[download_accordion, download_file],
    )
    
    # -------------------------------
    # PDF format
    # -------------------------------
    download_pdf_btn.click(
        fn=download_chat,
        inputs=[topic_input, output_box, gr.State("PDF")],
        outputs=[download_file],
    ).then(
        fn=lambda: (gr.update(visible=False, open=False), gr.update(visible=True)),
        inputs=None,
        outputs=[download_accordion, download_file],
    )
    
    # -------------------------------
    # Word format
    # -------------------------------
    download_docx_btn.click(
        fn=download_chat,
        inputs=[topic_input, output_box, gr.State("Word")],
        outputs=[download_file],
    ).then(
        fn=lambda: (gr.update(visible=False, open=False), gr.update(visible=True)),
        inputs=None,
        outputs=[download_accordion, download_file],
    )

