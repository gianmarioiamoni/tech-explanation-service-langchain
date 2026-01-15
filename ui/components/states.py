# ui/components/states.py
#
# Shared Gradio state components
#
# Responsibilities:
# - Define all gr.State components used across the app
# - Centralize state management

import gradio as gr


def create_shared_states():
    # Create all shared state components for the application
    #
    # Returns:
    #     Tuple of (history_state, rag_uploaded_state)
    
    history_state = gr.State([])  # Chat history
    rag_uploaded_state = gr.State([])  # Uploaded RAG documents
    
    return history_state, rag_uploaded_state

