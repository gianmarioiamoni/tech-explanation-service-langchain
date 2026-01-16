# ui/components/rag_section.py
#
# RAG document upload section components
#
# Responsibilities:
# - Create RAG file upload components
# - Create clear documents button
# - Create status display

import gradio as gr


def create_rag_section():
    # Create RAG document upload section with collapsible accordion
    #
    # Returns:
    #     Tuple of (file_upload, clear_btn, status_box)
    
    # Collapsible upload area
    with gr.Accordion("📚 Upload Documents for Context-Aware Answers (RAG)", open=False):
        file_upload = gr.File(
            label="📂 Select Files",
            file_types=[".pdf", ".txt", ".md", ".docx"],
            file_count="multiple",
            type="filepath",
        )
        with gr.Row():
            clear_btn = gr.Button(
                "🗑️ Clear All Documents",
                variant="secondary",
                scale=1,
            )
    
    # Status always visible
    status_box = gr.Textbox(
        label="📄 Uploaded Documents Status",
        lines=2,
        interactive=False,
        value="No documents uploaded.",
    )
    
    return file_upload, clear_btn, status_box

