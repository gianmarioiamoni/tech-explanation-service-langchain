# ui/gradio_app.py
#
# Gradio UI for the Tech Explanation Service
#
# Responsibilities:
# - Compose UI components from modular sections
# - Wire events using event modules
# - Launch the Gradio application
#
# Note: UI components are in ui/components/
#       Event wiring is in ui/events/
#       Business logic is in app/services/
#       Callbacks are in ui/callbacks/

import sys
from pathlib import Path

# Add project root to path to allow import of 'app'
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Logo paths
logo_svg_path = str(project_root / "assets" / "logo.svg")
logo_png_path = str(project_root / "assets" / "logo.png")

# Read logo SVG as base64 for inline embedding
import base64
with open(logo_svg_path, "rb") as f:
    logo_svg_base64 = base64.b64encode(f.read()).decode("utf-8")
logo_data_uri = f"data:image/svg+xml;base64,{logo_svg_base64}"

import gradio as gr

# Import UI component factories
from ui.components import (
    create_shared_states,
    create_rag_section,
    create_topic_section,
    create_buttons_section,
    create_history_section,
    create_quota_section,
)

# Import event wiring functions
from ui.events import (
    wire_initialization_events,
    wire_rag_events,
    wire_explanation_events,
    wire_history_events,
    wire_download_events,
    wire_auth_events,
)

# -------------------------------
# UI Composition
# -------------------------------
with gr.Blocks(title="Tech Explanation Service") as demo:
    # Header with Logo
    gr.HTML(f"""
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <img src="{logo_data_uri}" alt="Logo" style="width: 60px; height: 60px;">
            <div>
                <h1 style="margin: 0; font-size: 2em;">Tech Explanation Service</h1>
                <p style="margin: 5px 0 0 0; color: #666;">
                    Enter one or more technical topics (separated by commas) 
                    and receive a clear and structured explanation.
                </p>
                <p style="margin: 5px 0 0 0; color: #666;">
                    💡 <strong>Demo Mode</strong>: Using shared quota (20 requests, 10,000 tokens/day)
                </p>
            </div>
        </div>
    """)
    
    # -------------------------------
    # Create States
    # -------------------------------
    history_state, rag_uploaded_state = create_shared_states()
    
    # Create Quota Section state
    quota_display, user_session_state = create_quota_section()
    
    # -------------------------------
    # Layout
    # -------------------------------
    with gr.Row():
        # Left Column - Main Interaction
        with gr.Column(scale=2):
            # RAG Upload Section
            rag_file_upload, rag_clear_btn, rag_status_box = create_rag_section()
            
            # Topic Input Section
            topic_input, history_mode, output_box = create_topic_section()
            
            # Action Buttons Section
            (
                explain_btn,
                stop_btn,
                download_btn,
                clear_btn,
                download_accordion,
                download_md_btn,
                download_pdf_btn,
                download_docx_btn,
                download_file,
            ) = create_buttons_section()
        
        # Right Column - History Management
        with gr.Column(scale=1):
            (
                history_dropdown,
                search_box,
                delete_dropdown,
                delete_btn,
                clear_all_btn,
            ) = create_history_section()
    
    # -------------------------------
    # Event Wiring
    # -------------------------------
    
    # Initialization events
    wire_initialization_events(
        demo,
        history_state,
        history_dropdown,
        delete_dropdown,
        search_box,
        rag_uploaded_state,
        rag_status_box,
    )
    
    # RAG upload/clear events
    wire_rag_events(
        rag_file_upload,
        rag_clear_btn,
        rag_uploaded_state,
        rag_status_box,
    )
    
    # Explanation generation events
    wire_explanation_events(
        explain_btn,
        topic_input,
        stop_btn,
        download_btn,
        clear_btn,
        history_state,
        history_mode,
        rag_uploaded_state,
        output_box,
        history_dropdown,
        delete_dropdown,
        download_accordion,
        download_file,
        user_session_state,
        quota_display,
    )
    
    # History management events
    wire_history_events(
        search_box,
        history_dropdown,
        delete_dropdown,
        delete_btn,
        clear_all_btn,
        history_state,
        topic_input,
        output_box,
        download_btn,
    )
    
    # Download events
    wire_download_events(
        download_btn,
        download_accordion,
        download_md_btn,
        download_pdf_btn,
        download_docx_btn,
        download_file,
        topic_input,
        output_box,
    )
    
    # Authentication and quota events
    wire_auth_events(
        demo,
        user_session_state,
        quota_display,
    )

# Enable queue for streaming and cancels functionality
demo.queue()

if __name__ == "__main__":
    demo.launch()
