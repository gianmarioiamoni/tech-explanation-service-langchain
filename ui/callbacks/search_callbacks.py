# ui/callbacks/search_callbacks.py
#
# Callbacks for search functionality
#
# Responsibilities:
# - Filter history based on search query
# - Update dropdown with filtered results

import gradio as gr
from app.services.tech_explanation_service import TechExplanationService
from ui.utils.ui_messages import get_history_info_message

# Service instance
service = TechExplanationService()


def search_in_history(search_query, full_history):
    # Filter the history based on search query.
    #
    # Args:
    #     search_query: Text to search for in topics and explanations
    #     full_history: Complete chat history
    #
    # Returns:
    #     Dropdown update with filtered results
    
    print(f"🔍 Ricerca per: '{search_query}'")
    
    if not search_query.strip():
        # Show all the history
        filtered = full_history
        info_msg = get_history_info_message(len(full_history))
    else:
        filtered = service.search_history(search_query, full_history)
        if len(filtered) == 0:
            info_msg = f"🔍 No results for '{search_query}'"
        else:
            info_msg = f"🔍 {len(filtered)} results for {len(full_history)} chats - Open the dropdown to select a chat or a date"
    
    radio_choices, radio_value = service.create_history_choices(filtered)
    return gr.update(choices=radio_choices, value=radio_value, info=info_msg)

