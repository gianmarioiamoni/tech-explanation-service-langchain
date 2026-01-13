# ui/callbacks/download_callbacks.py
# Callbacks for document download functionality

import gradio as gr
from ui.utils.document_exporter import DocumentExporter


def download_chat(topic: str, output: str, format: str):
    # Generate and return downloadable file in specified format
    #
    # Args:
        #     topic: Chat topic/title
    #     output: Explanation text
    #     format: Export format ("Markdown", "PDF", "Word")
    #
    # Returns:
    #     File path for Gradio to serve as download, or None if export fails
    
    if not output or not output.strip():
        gr.Warning("No content to download")
        return None
    
    if not topic or not topic.strip():
        topic = "Tech Explanation"
    
    try:
        file_path, filename = DocumentExporter.export_chat(topic, output, format)
        gr.Info(f"✅ {format} file generated: {filename}")
        return file_path
    except ImportError as e:
        gr.Error(f"❌ {format} export not available: {str(e)}")
        return None
    except Exception as e:
        gr.Error(f"❌ Export failed: {str(e)}")
        return None

