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
    
    print(f"[DEBUG] download_chat called: format={format}, topic={topic[:50] if topic else 'None'}, output_len={len(output) if output else 0}")
    
    if not output or not output.strip():
        gr.Warning("⚠️ No content to download")
        return None
    
    if not topic or not topic.strip():
        topic = "Tech Explanation"
    
    try:
        print(f"[DEBUG] Calling DocumentExporter.export_chat for {format}")
        file_path, filename = DocumentExporter.export_chat(topic, output, format)
        print(f"[DEBUG] Export successful: {filename} at {file_path}")
        gr.Info(f"✅ {format} file generated: {filename}")
        return file_path
    except ImportError as e:
        print(f"[ERROR] Import error for {format}: {e}")
        gr.Error(f"❌ {format} export failed: Missing library. Check console for details.")
        return None
    except Exception as e:
        print(f"[ERROR] Export failed for {format}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        gr.Error(f"❌ {format} export failed: {str(e)}")
        return None

