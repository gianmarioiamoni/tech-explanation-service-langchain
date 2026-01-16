# ui/callbacks/history_callbacks.py
#
# Callbacks for chat history management
#
# Responsibilities:
# - Initialize history on page load
# - Load selected chat or date from history
# - Delete chat from history

import gradio as gr
from app.services.history import (
    HistoryRepository,
    HistoryFormatter,
    HistoryLoader,
)
from ui.utils.ui_messages import get_history_info_message

# Domain service instances
history_repository = HistoryRepository()
history_formatter = HistoryFormatter()
history_loader = HistoryLoader()


def initialize_history():
    # Initialize history when the page is loaded.
    # Loads history from Hugging Face Hub.
    # Args:
    #     None
    #
    # Returns:
    #     Tuple of (history, history_dropdown_update, delete_dropdown_update, search_box_clear)
    #
    # Returns:
    #     Tuple of (history, history_dropdown_update, delete_dropdown_update, search_box_clear)
    print("\n🔄 Initialization of new session...")
    fresh_history = history_repository.load_history()
    print(f"   📚 History loaded: {len(fresh_history)} items")
    
    radio_choices, radio_value = history_formatter.create_history_choices(fresh_history)
    delete_choices = history_formatter.create_delete_choices(fresh_history)
    
    # Dynamic info message
    info_msg = get_history_info_message(len(fresh_history))
    
    return fresh_history, gr.update(choices=radio_choices, value=radio_value, info=info_msg), gr.update(choices=delete_choices), ""


def load_selected_chat(selection, history):
    # Load a chat from history when selected from dropdown.
    #
    # Args:
    #     selection: Selected item from dropdown (can be a chat or a date header)
    #     history: Current chat history
    #
    # Returns:
    #     Tuple of (topic_text, explanation_text) or gr.update() if invalid
   
    # Guard: Ignore None or empty selection (happens during UI initialization)
    if not selection:
        return gr.update(), gr.update()
   
    # CASE 1: Is it a date? Show all chats for that day
    if "📅" in selection:
        # Extract the date from the format "📅 DD/MM/YYYY"
        date_str = selection.replace("📅", "").strip()
        print(f"📅 Data selezionata: '{date_str}' - caricamento chat del giorno...")
        
        chats = history_loader.get_chats_by_date(date_str, history)
        
        if chats:
            print(f"   Trovate {len(chats)} chat per {date_str}")
            combined_topic, combined_output = history_loader.format_chats_for_date(date_str, chats)
            return combined_topic, combined_output
        
        print(f"⚠️ Nessuna chat trovata per la data: '{date_str}'")
        return gr.update(), gr.update()
    
    # CASE 2: It's a single chat
    topic_display = HistoryFormatter.parse_topic_from_selection(selection)
    
    if not topic_display:
        print(f"⚠️ Selezione non valida: '{selection}'")
        return gr.update(), gr.update()
    
    # Find chat in history
    result = history_loader.find_chat_by_topic(topic_display, history)
    
    if result:
        topic, explanation = result
        print(f"✅ Chat singola caricata: {topic[:50]}")
        return topic, explanation
    
    print(f"⚠️ Chat non trovata per selezione: '{topic_display}'")
    return gr.update(), gr.update()


def delete_selected_chat(delete_selection, history, search_query):
    # Delete a chat from history.
    #
    # Args:
    #     delete_selection: Selected item from delete dropdown (format: "IDX. topic")
    #     history: Current chat history
    #     search_query: Current search query (unused, but kept for compatibility)
    #
    # Returns:
    #     Tuple of (new_history, history_dropdown_update, delete_dropdown_update, 
    #               delete_button_update, topic_clear, output_clear)
    
    if not delete_selection:
        return history, gr.update(), gr.update(), gr.update(), "", ""
    
    try:
        # Format: "IDX. topic"
        idx = int(delete_selection.split(".")[0].strip())
        
        if 0 <= idx < len(history):
            topic = history[idx][0]
            print(f"🗑️ Eliminazione chat {idx}: {topic}")
            
            new_history = history_repository.delete_from_history(idx, history)
            
            # Components update
            radio_choices, radio_value = history_formatter.create_history_choices(new_history)
            delete_choices = history_formatter.create_delete_choices(new_history)
            
            # Info message
            info_msg = get_history_info_message(len(new_history))
            
            return (
                new_history,
                gr.update(choices=radio_choices, value=None, info=info_msg),
                gr.update(choices=delete_choices, value=None),
                gr.update(interactive=False),  # Disable delete button after deletion
                "",
                "",
            )
    except Exception as e:
        print(f"❌ Errore eliminazione: {e}")
    
    return history, gr.update(), gr.update(), gr.update(), gr.update(), gr.update()


def clear_all_chats():
    # Clear all chats from history.
    #
    # Args:
    #     None
    #
    # Returns:
    #     Tuple of (empty_history, history_dropdown_update, delete_dropdown_update, 
    #               delete_button_update, topic_clear, output_clear)
    
    print("\n🧹 Clearing all chats from history...")
    
    # Save empty history to HF Hub
    empty_history = []
    history_repository.save_history(empty_history)
    
    # Update all dropdowns and UI components
    radio_choices, radio_value = history_formatter.create_history_choices(empty_history)
    delete_choices = history_formatter.create_delete_choices(empty_history)
    
    # Info message
    info_msg = get_history_info_message(len(empty_history))
    
    print(f"✅ All chats cleared")
    
    return (
        empty_history,
        gr.update(choices=radio_choices, value=None, info=info_msg),
        gr.update(choices=delete_choices, value=None),
        gr.update(interactive=False),  # Disable delete button
        "",
        "",
    )

