# ui/components/buttons_section.py
#
# Action buttons section components
#
# Responsibilities:
# - Create Explain, Stop, Download, Clear buttons
# - Create download format selection accordion
# - Create download file component

import gradio as gr


def create_buttons_section():
    # Create action buttons row and download components
    #
    # Returns:
    #     Tuple of (explain_btn, stop_btn, download_btn, clear_btn,
    #               download_accordion, download_md_btn, download_pdf_btn, 
    #               download_docx_btn, download_file)
    
    # Main action buttons
    with gr.Row():
        explain_btn = gr.Button(
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
        clear_btn = gr.Button(
            "🔄 Clear",
            variant="secondary",
            scale=1,
        )
    
    # Download format submenu
    download_accordion = gr.Accordion("📥 Select Format", open=True, visible=False)
    with download_accordion:
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
    
    # Download file component
    download_file = gr.File(
        label="Download your file",
        visible=False,
        interactive=False,
    )
    
    return (
        explain_btn,
        stop_btn,
        download_btn,
        clear_btn,
        download_accordion,
        download_md_btn,
        download_pdf_btn,
        download_docx_btn,
        download_file,
    )

