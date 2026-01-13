import sys
from pathlib import Path

# Aggiungi project root al path per permettere import di 'app'
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gradio as gr
from app.services.tech_explanation_service import TechExplanationService
from datetime import datetime

# -------------------------------
# Inizializzazione servizio
# -------------------------------
service = TechExplanationService()

# -------------------------------
# Callback streaming
# -------------------------------
def explain_topic_stream(topic: str, history):
    topic_clean = (topic or "").strip()
    if not topic_clean:
        yield history, "Please enter a technical topic.", gr.update(), gr.update()
        return

    print(f"\n{'='*60}")
    print(f"🚀 Nuova richiesta: '{topic_clean}'")
    print(f"   History corrente: {len(history)} items")

    # Accumula i chunk RAW dallo streaming
    accumulated_raw = ""
    for chunk in service.explain_stream(topic_clean):
        accumulated_raw = chunk
        yield history, accumulated_raw, gr.update(), gr.update()

    # Sanitizzazione finale con paragrafi
    final_text = service._sanitize_output(accumulated_raw)
    print(f"   ✅ Generazione completata: {len(final_text)} chars")

    # Aggiorna history e salva su HF (con error handling integrato)
    new_history = service.add_to_history(topic_clean, final_text, history)
    print(f"   📚 History aggiornata: {len(new_history)} items (era {len(history)})")

    # Aggiorna i componenti
    radio_choices, radio_value = create_history_choices(new_history)
    delete_choices = [f"🗑️ {i}: {truncate(h[0], 40)}" for i, h in enumerate(new_history)]
    
    print(f"   🔄 History display aggiornato con {len(new_history)} items")
    print(f"{'='*60}\n")
    
    yield new_history, final_text, gr.update(choices=radio_choices), gr.update(choices=delete_choices)


# -------------------------------
# Helper functions
# -------------------------------
def truncate(text: str, max_len: int) -> str:
    """Tronca il testo a max_len caratteri"""
    return text[:max_len] + "..." if len(text) > max_len else text


def create_history_choices(history):
    """Crea le scelte per il radio button raggruppate per data"""
    if not history:
        return ["📭 Nessuna chat salvata"], None
    
    # Raggruppa per data
    grouped = service.group_by_date(history)
    
    choices = []
    for date_key, chats in grouped.items():
        date_label = chats[0]["date_label"]
        # Header data (non selezionabile, solo visivo)
        choices.append(f"━━━ 📅 {date_label} ━━━")
        
        # Chat items
        for chat in chats:
            topic = truncate(chat["topic"], 50)
            # Trova l'indice originale
            original_idx = None
            for idx, item in enumerate(history):
                if len(item) >= 2 and item[0] == chat["topic"]:
                    if len(item) == 3 and item[2] == chat["timestamp"]:
                        original_idx = idx
                        break
                    elif len(item) == 2:
                        original_idx = idx
                        break
            
            choices.append(f"   {original_idx}: {topic}")
    
    return choices, None


def parse_selection(selection: str):
    """Estrae l'indice dalla selezione"""
    if not selection or "━━━" in selection:
        return None
    try:
        # Formato: "   IDX: topic"
        idx_str = selection.strip().split(":")[0].strip()
        return int(idx_str)
    except:
        return None


# -------------------------------
# Caricamento iniziale history
# -------------------------------
def initialize_history():
    """Carica l'history da HF Hub quando la pagina viene aperta"""
    print("\n🔄 Inizializzazione nuova sessione...")
    fresh_history = service.load_history()
    print(f"   📚 History caricata: {len(fresh_history)} items")
    
    radio_choices, radio_value = create_history_choices(fresh_history)
    delete_choices = [f"🗑️ {i}: {truncate(h[0], 40)}" for i, h in enumerate(fresh_history)] if fresh_history else []
    
    return fresh_history, gr.update(choices=radio_choices, value=radio_value), gr.update(choices=delete_choices), ""


# -------------------------------
# Callback per ricerca
# -------------------------------
def search_in_history(search_query, full_history):
    """Filtra la history in base alla query di ricerca"""
    print(f"🔍 Ricerca per: '{search_query}'")
    
    if not search_query.strip():
        # Mostra tutta la history
        filtered = full_history
    else:
        filtered = service.search_history(search_query, full_history)
    
    radio_choices, radio_value = create_history_choices(filtered)
    return gr.update(choices=radio_choices, value=radio_value)


# -------------------------------
# Callback per selezione chat
# -------------------------------
def load_selected_chat(selection, history):
    """Carica una chat dall'history quando selezionata"""
    idx = parse_selection(selection)
    if idx is not None and 0 <= idx < len(history):
        item = history[idx]
        topic = item[0]
        explanation = item[1]
        print(f"✅ Chat {idx} caricata: {topic[:50]}")
        return topic, explanation
    return gr.update(), gr.update()


# -------------------------------
# Callback per delete
# -------------------------------
def delete_selected_chat(delete_selection, history, search_query):
    """Elimina una chat dall'history"""
    if not delete_selection:
        return history, gr.update(), gr.update(), "", ""
    
    try:
        # Formato: "🗑️ IDX: topic"
        idx = int(delete_selection.split(":")[0].replace("🗑️", "").strip())
        
        if 0 <= idx < len(history):
            topic = history[idx][0]
            print(f"🗑️ Eliminazione chat {idx}: {topic}")
            
            new_history = service.delete_from_history(idx, history)
            
            # Aggiorna i componenti
            radio_choices, radio_value = create_history_choices(new_history)
            delete_choices = [f"🗑️ {i}: {truncate(h[0], 40)}" for i, h in enumerate(new_history)] if new_history else []
            
            return new_history, gr.update(choices=radio_choices, value=None), gr.update(choices=delete_choices, value=None), "", ""
    except Exception as e:
        print(f"❌ Errore eliminazione: {e}")
    
    return history, gr.update(), gr.update(), gr.update(), gr.update()


# -------------------------------
# UI
# -------------------------------
with gr.Blocks(title="Tech Explanation Service") as demo:
    gr.Markdown(
        "# 🎓 Tech Explanation Service\nInserisci un topic tecnico e ricevi una spiegazione chiara e strutturata."
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
            
            # History list (con raggruppamento per data)
            history_radio = gr.Radio(
                label="Select a chat",
                choices=["⏳ Loading..."],
                value=None,
                interactive=True,
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
    # Eventi
    # -------------------------------
    
    # Caricamento iniziale
    demo.load(
        fn=initialize_history,
        inputs=None,
        outputs=[history_state, history_radio, delete_dropdown, search_box],
    )
    
    # Ricerca
    search_box.change(
        fn=search_in_history,
        inputs=[search_box, history_state],
        outputs=[history_radio],
    )
    
    # Selezione chat dalla history
    history_radio.change(
        fn=load_selected_chat,
        inputs=[history_radio, history_state],
        outputs=[topic_input, output_box],
    )
    
    # Explain
    explain_button.click(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state],
        outputs=[history_state, output_box, history_radio, delete_dropdown],
    )

    topic_input.submit(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state],
        outputs=[history_state, output_box, history_radio, delete_dropdown],
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
        outputs=[history_state, history_radio, delete_dropdown, topic_input, output_box],
    )


if __name__ == "__main__":
    demo.launch()
