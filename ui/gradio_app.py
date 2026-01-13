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
    delete_choices = [f"{i}. {truncate(h[0], 50)}" for i, h in enumerate(new_history)]
    
    # Info message
    info_msg = f"💬 {len(new_history)} chat disponibili - Seleziona una chat o una data per visualizzare"
    
    print(f"   🔄 History display aggiornato con {len(new_history)} items")
    print(f"{'='*60}\n")
    
    yield new_history, final_text, gr.update(choices=radio_choices, info=info_msg), gr.update(choices=delete_choices)


# -------------------------------
# Helper functions
# -------------------------------
def truncate(text: str, max_len: int) -> str:
    """Tronca il testo a max_len caratteri"""
    return text[:max_len] + "..." if len(text) > max_len else text


def create_history_choices(history):
    """Crea le scelte per il dropdown raggruppate per data
    
    Usa un formato che simula optgroup HTML:
    - Date come separatori visivi (prefisso speciale per identificarle)
    - Chat indentate sotto ogni data
    """
    if not history:
        return ["📭 Nessuna chat salvata"], None
    
    # Raggruppa per data
    grouped = service.group_by_date(history)
    
    choices = []
    
    for date_key, chats in grouped.items():
        date_label = chats[0]["date_label"]
        
        # Header data - solo emoji calendario come identificatore
        date_header = f"📅 {date_label}"
        choices.append(date_header)
        
        # Chat items sotto la data - solo indentazione, no bullet points
        for chat in chats:
            topic_display = truncate(chat["topic"], 60)
            # Solo 2 spazi per indentazione visiva
            choices.append(f"  {topic_display}")
    
    return choices, None


def parse_topic_from_selection(selection: str):
    """Estrae il topic dalla selezione formato '  Topic'
    
    Returns il topic pulito, o None se è un header data o selezione non valida
    """
    if not selection:
        return None
    
    # Ignora headers data (contengono emoji calendario)
    if "📅" in selection:
        return None
    
    # Ignora messaggi speciali
    if "📭" in selection:
        return None
    
    # Rimuovi spazi iniziali (indentazione)
    topic = selection.strip()
    
    # Se vuoto dopo lo strip, non è valido
    if not topic:
        return None
    
    return topic


# -------------------------------
# Caricamento iniziale history
# -------------------------------
def initialize_history():
    """Carica l'history da HF Hub quando la pagina viene aperta"""
    print("\n🔄 Inizializzazione nuova sessione...")
    fresh_history = service.load_history()
    print(f"   📚 History caricata: {len(fresh_history)} items")
    
    radio_choices, radio_value = create_history_choices(fresh_history)
    # Delete dropdown: mantieni numeri per identificazione univoca
    delete_choices = [f"{i}. {truncate(h[0], 50)}" for i, h in enumerate(fresh_history)] if fresh_history else []
    
    # Info message dinamico
    if len(fresh_history) == 0:
        info_msg = "📭 Nessuna chat salvata"
    elif len(fresh_history) == 1:
        info_msg = "💬 1 chat disponibile - Seleziona una chat o una data per visualizzare"
    else:
        info_msg = f"💬 {len(fresh_history)} chat disponibili - Seleziona una chat o una data per visualizzare"
    
    return fresh_history, gr.update(choices=radio_choices, value=radio_value, info=info_msg), gr.update(choices=delete_choices), ""


# -------------------------------
# Callback per ricerca
# -------------------------------
def search_in_history(search_query, full_history):
    """Filtra la history in base alla query di ricerca"""
    print(f"🔍 Ricerca per: '{search_query}'")
    
    if not search_query.strip():
        # Mostra tutta la history
        filtered = full_history
        info_msg = f"💬 {len(full_history)} chat disponibili - Seleziona una chat o una data per visualizzare"
    else:
        filtered = service.search_history(search_query, full_history)
        if len(filtered) == 0:
            info_msg = f"🔍 Nessun risultato per '{search_query}'"
        else:
            info_msg = f"🔍 {len(filtered)} risultati di {len(full_history)} chat - Seleziona per visualizzare"
    
    radio_choices, radio_value = create_history_choices(filtered)
    return gr.update(choices=radio_choices, value=radio_value, info=info_msg)


# -------------------------------
# Callback per selezione chat o data
# -------------------------------
def load_selected_chat(selection, history):
    """Carica una chat dall'history quando selezionata, o tutte le chat di una data"""
    
    # CASO 1: È una data? Mostra tutte le chat di quel giorno
    if selection and "📅" in selection:
        # Estrai la data dal formato "📅 DD/MM/YYYY"
        date_str = selection.replace("📅", "").strip()
        print(f"📅 Data selezionata: '{date_str}' - caricamento chat del giorno...")
        
        # Raggruppa per data
        grouped = service.group_by_date(history)
        
        # Cerca il gruppo corrispondente
        for date_key, chats in grouped.items():
            if chats[0]["date_label"] == date_str:
                print(f"   Trovate {len(chats)} chat per {date_str}")
                
                # Crea un output combinato con tutte le chat del giorno
                combined_output = f"📅 Chat del {date_str}\n"
                combined_output += "=" * 60 + "\n\n"
                
                for i, chat in enumerate(chats, 1):
                    combined_output += f"🔹 Chat {i}: {chat['topic']}\n"
                    combined_output += "─" * 60 + "\n"
                    combined_output += chat['explanation'] + "\n\n"
                    if i < len(chats):
                        combined_output += "\n"
                
                # Ritorna un topic descrittivo e l'output combinato
                combined_topic = f"📅 {date_str} ({len(chats)} chat)"
                return combined_topic, combined_output
        
        print(f"⚠️ Nessuna chat trovata per la data: '{date_str}'")
        return gr.update(), gr.update()
    
    # CASO 2: È una chat singola
    topic_display = parse_topic_from_selection(selection)
    
    if not topic_display:
        print(f"⚠️ Selezione non valida: '{selection}'")
        return gr.update(), gr.update()
    
    # Cerca nella history per topic
    # Se il topic è troncato (finisce con ...), cerca per prefisso
    is_truncated = topic_display.endswith("...")
    
    for item in history:
        topic = item[0]
        explanation = item[1]
        
        if is_truncated:
            # Match parziale (senza i ...)
            topic_prefix = topic_display[:-3]  # Rimuovi "..."
            if topic.startswith(topic_prefix):
                print(f"✅ Chat singola caricata (match parziale): {topic[:50]}")
                return topic, explanation
        else:
            # Match esatto
            if topic == topic_display:
                print(f"✅ Chat singola caricata: {topic[:50]}")
                return topic, explanation
    
    # Se non trovato, prova un match case-insensitive
    topic_lower = topic_display.lower().replace("...", "")
    for item in history:
        topic = item[0]
        if topic.lower().startswith(topic_lower):
            print(f"✅ Chat singola caricata (match case-insensitive): {topic[:50]}")
            return topic, item[1]
    
    print(f"⚠️ Chat non trovata per selezione: '{topic_display}'")
    return gr.update(), gr.update()


# -------------------------------
# Callback per delete
# -------------------------------
def delete_selected_chat(delete_selection, history, search_query):
    """Elimina una chat dall'history"""
    if not delete_selection:
        return history, gr.update(), gr.update(), "", ""
    
    try:
        # Formato: "IDX. topic"
        idx = int(delete_selection.split(".")[0].strip())
        
        if 0 <= idx < len(history):
            topic = history[idx][0]
            print(f"🗑️ Eliminazione chat {idx}: {topic}")
            
            new_history = service.delete_from_history(idx, history)
            
            # Aggiorna i componenti
            radio_choices, radio_value = create_history_choices(new_history)
            delete_choices = [f"{i}. {truncate(h[0], 50)}" for i, h in enumerate(new_history)] if new_history else []
            
            # Info message
            if len(new_history) == 0:
                info_msg = "📭 Nessuna chat salvata"
            else:
                info_msg = f"💬 {len(new_history)} chat disponibili - Seleziona una chat o una data per visualizzare"
            
            return new_history, gr.update(choices=radio_choices, value=None, info=info_msg), gr.update(choices=delete_choices, value=None), "", ""
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
            
            # History list (dropdown con raggruppamento per data)
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
    # Eventi
    # -------------------------------
    
    # Caricamento iniziale
    demo.load(
        fn=initialize_history,
        inputs=None,
        outputs=[history_state, history_dropdown, delete_dropdown, search_box],
    )
    
    # Ricerca
    search_box.change(
        fn=search_in_history,
        inputs=[search_box, history_state],
        outputs=[history_dropdown],
    )
    
    # Selezione chat dalla history
    history_dropdown.change(
        fn=load_selected_chat,
        inputs=[history_dropdown, history_state],
        outputs=[topic_input, output_box],
    )
    
    # Explain
    explain_button.click(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state],
        outputs=[history_state, output_box, history_dropdown, delete_dropdown],
    )

    topic_input.submit(
        fn=explain_topic_stream,
        inputs=[topic_input, history_state],
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
