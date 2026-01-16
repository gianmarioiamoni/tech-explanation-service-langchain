# ui/components/history_section.py
#
# History management section components
#
# Responsibilities:
# - Create history dropdown
# - Create search box
# - Create delete section (accordion, dropdown, buttons)

import gradio as gr


def create_history_section():
    # Create history management section with search and delete
    #
    # Returns:
    #     Tuple of (history_dropdown, search_box, delete_dropdown, 
    #               delete_btn, clear_all_btn)
    
    gr.Markdown("---")
    
    # History dropdown
    history_dropdown = gr.Dropdown(
        label="💬 Chat History",
        choices=[],
        value=None,
        interactive=True,
        allow_custom_value=False,
    )
    
    # Search box
    search_box = gr.Textbox(
        label="🔍 Search in history",
        placeholder="Search for a topic...",
        lines=1,
    )
    
    gr.Markdown("---")
    
    # Delete section
    with gr.Accordion("🗑️ Delete Chat", open=False):
        delete_dropdown = gr.Dropdown(
            label="Select chat to delete",
            choices=[],
            value=None,
            interactive=True,
        )
        with gr.Row():
            delete_btn = gr.Button(
                "🗑️ Delete Selected",
                variant="stop",
                scale=1,
                interactive=False,  # Disabled by default
            )
            clear_all_btn = gr.Button(
                "🧹 Clear All Chats",
                variant="stop",
                scale=1,
            )
    
    return history_dropdown, search_box, delete_dropdown, delete_btn, clear_all_btn

