# ui/events/history_events.py
#
# History management events
#
# Responsibilities:
# - Wire search box event
# - Wire history dropdown selection event
# - Wire delete button event
# - Wire clear all button event

import gradio as gr
from ui.callbacks import load_selected_chat, delete_selected_chat, clear_all_chats, search_in_history


def wire_history_events(search_box, history_dropdown, delete_dropdown, delete_btn, 
                        clear_all_btn, history_state, topic_input, output_box, download_btn):
    # Wire all history management events
    #
    # Args:
    #     search_box: gr.Textbox for searching history
    #     history_dropdown: gr.Dropdown for selecting chats
    #     delete_dropdown: gr.Dropdown for selecting chat to delete
    #     delete_btn: gr.Button for deleting selected chat
    #     clear_all_btn: gr.Button for clearing all chats
    #     history_state: gr.State for chat history
    #     topic_input: gr.Textbox for topic display
    #     output_box: gr.Textbox for explanation display
    #     download_btn: gr.Button for download (to enable/disable)
    
    # -------------------------------
    # Search box
    # -------------------------------
    search_box.change(
        fn=search_in_history,
        inputs=[search_box, history_state],
        outputs=[history_dropdown],
    )
    
    # -------------------------------
    # History dropdown selection
    # -------------------------------
    history_dropdown.change(
        fn=load_selected_chat,
        inputs=[history_dropdown, history_state],
        outputs=[topic_input, output_box],
    ).then(
        fn=lambda text: gr.update(interactive=bool(text)),
        inputs=[output_box],
        outputs=[download_btn],
    )
    
    # -------------------------------
    # Delete dropdown selection (enable/disable delete button)
    # -------------------------------
    delete_dropdown.change(
        fn=lambda x: gr.update(interactive=bool(x)),
        inputs=[delete_dropdown],
        outputs=[delete_btn],
    )
    
    # -------------------------------
    # Delete selected chat
    # -------------------------------
    delete_btn.click(
        fn=delete_selected_chat,
        inputs=[delete_dropdown, history_state, search_box],
        outputs=[history_state, history_dropdown, delete_dropdown, delete_btn, topic_input, output_box],
    )
    
    # -------------------------------
    # Clear all chats
    # -------------------------------
    clear_all_btn.click(
        fn=clear_all_chats,
        inputs=None,
        outputs=[history_state, history_dropdown, delete_dropdown, delete_btn, topic_input, output_box],
    )

