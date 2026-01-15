# ui/events/rag_events.py
#
# RAG document upload/clear events
#
# Responsibilities:
# - Wire file upload event
# - Wire clear documents event

from ui.callbacks.upload_callbacks import upload_documents, clear_rag_index


def wire_rag_events(rag_file_upload, rag_clear_btn, rag_uploaded_state, rag_status_box):
    # Wire all RAG-related events
    #
    # Args:
    #     rag_file_upload: gr.File for document upload
    #     rag_clear_btn: gr.Button for clearing documents
    #     rag_uploaded_state: gr.State for tracking uploaded docs
    #     rag_status_box: gr.Textbox for status display
    
    # Upload documents
    rag_file_upload.upload(
        fn=upload_documents,
        inputs=[rag_file_upload, rag_uploaded_state],
        outputs=[rag_uploaded_state, rag_status_box],
    )
    
    # Clear all documents
    rag_clear_btn.click(
        fn=clear_rag_index,
        inputs=[rag_uploaded_state],
        outputs=[rag_uploaded_state, rag_status_box],
    )

