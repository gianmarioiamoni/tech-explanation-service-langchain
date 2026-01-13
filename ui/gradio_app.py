# ui/gradio_app.py
#
# Gradio UI for the Tech Explanation Service
# Streaming + Persistent History + Dropdown + Primary Button
#
# Responsibilities:
# - Provide a web interface for the Tech Explanation Service
# - Handle streaming of the output
# - Handle the history of the chats
# - Handle the dropdown of the previous chats
# - Handle the primary button to explain the topic
import sys
from pathlib import Path

# Add project root to path to allow import of 'app'
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gradio as gr
from app.services.tech_explanation_service import TechExplanationService
from datetime import datetime

# -------------------------------
# Constants for UI messages
# -------------------------------
MSG_NO_CHATS = "📭 No chats saved"
MSG_ONE_CHAT = "💬 1 available chat - Open the dropdown to select a chat or a date"
MSG_MULTIPLE_CHATS = "💬 {count} available chats - Open the dropdown to select a chat or a date"

def get_history_info_message(history_count: int) -> str:
    """Generate appropriate info message based on history count"""
    if history_count == 0:
        return MSG_NO_CHATS
    elif history_count == 1:
        return MSG_ONE_CHAT
    else:
        return MSG_MULTIPLE_CHATS.format(count=history_count)

# -------------------------------
# Inizializzazione servizio
# -------------------------------
service = TechExplanationService()

# -------------------------------
# Callback streaming
# -------------------------------
def explain_topic_stream(topic: str, history, history_mode: str):
    topic_clean = (topic or "").strip()
    if not topic_clean:
        yield history, "Please enter at least one technical topic.", gr.update(), gr.update()
        return

    print(f"\n{'='*60}")
    print(f"🚀 Multi-topic request: '{topic_clean}'")

    # Parse topics to maintain order
    topics = service.parse_topics(topic_clean)
    topic_contents = {}  # Dictionary to track accumulated content per topic
    aggregate_mode = history_mode == "Aggregate into one chat"

    for topic_name, accumulated_text in service.explain_multiple_stream(topic_clean):
        # Note: accumulated_text is already the FULL text for this topic (not incremental)
        # Store the latest accumulated text for this topic
        topic_contents[topic_name] = accumulated_text

        if aggregate_mode:
            # Aggregate mode: use service method to combine topics
            accumulated_raw = service.aggregate_topics_output(topics, topic_contents)
        else:
            # Separate mode: show only current topic
            accumulated_raw = f"{topic_name}:\n\n{accumulated_text}"
        
        yield history, accumulated_raw, gr.update(), gr.update()

    # Final sanitization
    final_text = service._sanitize_output(accumulated_raw)

    if history_mode == "Aggregate into one chat":
        # Single aggregated chat
        history = service.add_to_history(topic_clean, final_text, history)
    else:
        # One chat per topic (current behavior)
        for t in topics:
            history = service.add_to_history(t, final_text, history)

    radio_choices, _ = service.create_history_choices(history)
    delete_choices = service.create_delete_choices(history)

    info_msg = get_history_info_message(len(history))

    print(f"✅ Multi-topic generation completed")
    print(f"{'='*60}\n")

    yield history, final_text, gr.update(choices=radio_choices, info=info_msg), gr.update(choices=delete_choices)


# -------------------------------
# Initialization of history
# -------------------------------
def initialize_history():
    # Load the history from HF Hub when the page is opened
    print("\n🔄 Inizializzazione nuova sessione...")
    fresh_history = service.load_history()
    print(f"   📚 History caricata: {len(fresh_history)} items")
    
    radio_choices, radio_value = service.create_history_choices(fresh_history)
    delete_choices = service.create_delete_choices(fresh_history)
    
    # Dynamic info message
    info_msg = get_history_info_message(len(fresh_history))
    
    return fresh_history, gr.update(choices=radio_choices, value=radio_value, info=info_msg), gr.update(choices=delete_choices), ""


# -------------------------------
# Callback for search
# -------------------------------
def search_in_history(search_query, full_history):
    # Filter the history based on the search query
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


# -------------------------------
# Callback for selected chat or date
# -------------------------------
def load_selected_chat(selection, history):
    # Load a chat from the history when selected, or all the chats of a date
    
    # CASE 1: Is it a date? Show all chats for that day
    if selection and "📅" in selection:
        # Extract the date from the format "📅 DD/MM/YYYY"
        date_str = selection.replace("📅", "").strip()
        print(f"📅 Data selezionata: '{date_str}' - caricamento chat del giorno...")
        
        chats = service.get_chats_by_date(date_str, history)
        
        if chats:
            print(f"   Trovate {len(chats)} chat per {date_str}")
            combined_topic, combined_output = service.format_chats_for_date(date_str, chats)
            return combined_topic, combined_output
        
        print(f"⚠️ Nessuna chat trovata per la data: '{date_str}'")
        return gr.update(), gr.update()
    
    # CASE 2: It's a single chat
    topic_display = service.parse_topic_from_selection(selection)
    
    if not topic_display:
        print(f"⚠️ Selezione non valida: '{selection}'")
        return gr.update(), gr.update()
    
    # Find chat in history
    result = service.find_chat_by_topic(topic_display, history)
    
    if result:
        topic, explanation = result
        print(f"✅ Chat singola caricata: {topic[:50]}")
        return topic, explanation
    
    print(f"⚠️ Chat non trovata per selezione: '{topic_display}'")
    return gr.update(), gr.update()


# -------------------------------
# Callback for delete
# -------------------------------
def delete_selected_chat(delete_selection, history, search_query):
    # Delete a chat from the history
    if not delete_selection:
        return history, gr.update(), gr.update(), "", ""
    
    try:
        # Format: "IDX. topic"
        idx = int(delete_selection.split(".")[0].strip())
        
        if 0 <= idx < len(history):
            topic = history[idx][0]
            print(f"🗑️ Eliminazione chat {idx}: {topic}")
            
            new_history = service.delete_from_history(idx, history)
            
            # Components update
            radio_choices, radio_value = service.create_history_choices(new_history)
            delete_choices = service.create_delete_choices(new_history)
            
            # Info message
            info_msg = get_history_info_message(len(new_history))
            
            return new_history, gr.update(choices=radio_choices, value=None, info=info_msg), gr.update(choices=delete_choices, value=None), "", ""
    except Exception as e:
        print(f"❌ Errore eliminazione: {e}")
    
    return history, gr.update(), gr.update(), gr.update(), gr.update()


# -------------------------------
# UI
# -------------------------------
with gr.Blocks(title="Tech Explanation Service") as demo:
    gr.Markdown(
        "# 🎓 Tech Explanation Service\nEnter one or more technical topics (separated by commas) \nand receive a clear and structured explanation."
    )

    # State
    history_state = gr.State([])

    with gr.Row():
        with gr.Column(scale=2):
            topic_input = gr.Textbox(
                label="📝 Technical Topic",
                placeholder="e.g., Python decorators, Docker networking, RAG architecture",
                lines=1,
            )

            history_mode = gr.Radio(
                label="Multi-topic behavior",
                choices=[
                    "Aggregate into one chat",
                    "Save each topic as a separate chat"
                ],
                value="Aggregate into one chat",
            )

            output_box = gr.Textbox(
                label="💡 Explanation",
                lines=18,
                interactive=False,
            )

            with gr.Row():
                explain_button = gr.Button(
                    "✨ Explain",
                    variant="primary",
                    scale=1,
                )
                clear_button = gr.Button(
                    "🔄 Clear",
                    variant="secondary",
                    scale=0,
                )

        with gr.Column(scale=1):
            gr.Markdown("### 📚 Chat History")
            
            # Search box
            search_box = gr.Textbox(
                label="🔍 Search",
                placeholder="Search in chats...",
                lines=1,
            )
            
            # History list (dropdown grouped by date)
            history_dropdown = gr.Dropdown(
                label="📚 Previous chats (newest first)",
                choices=["⏳ Loading..."],
                value=None,
                interactive=True,
                allow_custom_value=False,
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
                delete_button = gr.Button(
                    "🗑️ Delete Selected",
                    variant="stop",
                )

    # -------------------------------
    # Events
    # -------------------------------
    
    # Initialization
    demo.load(
        fn=initialize_history,
        inputs=None,
        outputs=[history_state, history_dropdown, delete_dropdown, search_box],
    )
    
    # Search
    search_box.change(
        fn=search_in_history,
        inputs=[search_box, history_state],
        outputs=[history_dropdown],
    )
    
    # Selection of chat from the history
    history_dropdown.change(
        fn=load_selected_chat,
        inputs=[history_dropdown, history_state],
        outputs=[topic_input, output_box],
    )
    
    # Explain
    explain_button.click(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state, history_mode],
        outputs=[history_state, output_box, history_dropdown, delete_dropdown],
    )

    topic_input.submit(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state, history_mode],
        outputs=[history_state, output_box, history_dropdown, delete_dropdown],
    )
    
    # Clear
    clear_button.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[topic_input, output_box],
    )
    
    # Delete
    delete_button.click(
        fn=delete_selected_chat,
        inputs=[delete_dropdown, history_state, search_box],
        outputs=[history_state, history_dropdown, delete_dropdown, topic_input, output_box],
    )


if __name__ == "__main__":
    demo.launch()
