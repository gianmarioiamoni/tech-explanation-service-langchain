# ui/events/initialization.py
#
# App initialization events
#
# Responsibilities:
# - Wire demo.load() events for history, Chroma, and RAG registry

from ui.callbacks import initialize_history
from ui.callbacks.rag_callbacks import initialize_chroma_vectorstore, initialize_rag_registry


def wire_initialization_events(demo, history_state, history_dropdown, delete_dropdown, 
                               search_box, rag_uploaded_state, rag_status_box):
    # Wire all initialization events that run on app load
    #
    # Args:
    #     demo: Gradio Blocks instance
    #     history_state: gr.State for chat history
    #     history_dropdown: gr.Dropdown for history selection
    #     delete_dropdown: gr.Dropdown for delete selection
    #     search_box: gr.Textbox for search
    #     rag_uploaded_state: gr.State for RAG documents
    #     rag_status_box: gr.Textbox for RAG status
    
    # Initialize history
    demo.load(
        fn=initialize_history,
        inputs=None,
        outputs=[history_state, history_dropdown, delete_dropdown, search_box],
    )
    
    # Initialize Chroma vectorstore from HF Hub
    demo.load(
        fn=initialize_chroma_vectorstore,
        inputs=None,
        outputs=None,
    )
    
    # Initialize RAG document registry
    demo.load(
        fn=initialize_rag_registry,
        inputs=None,
        outputs=[rag_uploaded_state, rag_status_box],
    )

