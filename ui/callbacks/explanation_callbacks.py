# ui/callbacks/explanation_callbacks.py
#
# Callbacks for topic explanation functionality (with RAG integration)
#
# Responsibilities:
# - Handle streaming explanation generation
# - Integrate RAGService for context-aware responses
# - Manage multi-topic vs single-topic modes
# - Update history after explanation

import gradio as gr
from app.services.explanation import ExplanationService, OutputFormatter
from app.services.history import HistoryRepository, HistoryFormatter
from ui.utils.ui_messages import get_history_info_message
from ui.callbacks.shared_services import rag_service  # Shared instance

# Domain service instances
explanation_service = ExplanationService()
# rag_service imported from shared_services (singleton)
output_formatter = OutputFormatter()
history_repository = HistoryRepository()
history_formatter = HistoryFormatter()


def explain_topic_stream(topic: str, history, history_mode: str, rag_uploaded_state=None):
    # Stream explanation with Conditional RAG support.
    #
    # Args:
    #     topic: Technical topic(s) to explain (comma-separated for multiple)
    #     history: Current chat history
    #     history_mode: "Aggregate into one chat" or "Save each topic as a separate chat"
    #     rag_uploaded_state: Unused (kept for Gradio signature compatibility)
    #
    # Yields:
    #     Tuple of (history, output_text, history_dropdown_update, delete_dropdown_update)
    #
    # Note: RAGService internally handles document availability check via has_documents()

    topic_clean = (topic or "").strip()
    if not topic_clean:
        yield history, "Please enter at least one technical topic.", gr.update(), gr.update()
        return

    print(f"\n{'='*60}")
    print(f"🚀 Multi-topic request: '{topic_clean}'")

    topics = output_formatter.parse_topics(topic_clean)
    topic_contents = {}
    topic_modes = {}  # Track mode for each topic
    aggregate_mode = history_mode == "Aggregate into one chat"

    # Stream each topic
    for topic_name in topics:
        # Use RAGService streaming (Conditional RAG logic handles everything)
        # - If docs uploaded + topic covered → RAG chain (streaming)
        # - Otherwise → Generic LLM chain (streaming)
        
        accumulated_for_topic = ""
        mode = None
        
        for accumulated_chunk, chunk_mode in rag_service.explain_topic_stream(topic_name):
            accumulated_for_topic = accumulated_chunk
            mode = chunk_mode
            
            # Store partial result
            topic_contents[topic_name] = accumulated_for_topic
            topic_modes[topic_name] = mode
            
            # Prepare text for streaming
            if aggregate_mode:
                accumulated_raw = output_formatter.aggregate_topics_output(topics, topic_contents)
            else:
                accumulated_raw = f"{topic_name}:\n\n{accumulated_for_topic}"
            
            # Add provisional badge during streaming
            streaming_badge = "⏳ Generating...\n\n"
            streamed_output = streaming_badge + accumulated_raw
            
            yield history, streamed_output, gr.update(), gr.update()
        
        # Sanitize final output for this topic
        topic_contents[topic_name] = output_formatter.sanitize_output(accumulated_for_topic)

    # Final aggregation
    final_text = output_formatter.aggregate_topics_output(topics, topic_contents)
    
    # Add badge based on mode
    # If all topics used RAG, show RAG badge; if any used generic, show generic badge
    used_rag = any(mode == "rag" for mode in topic_modes.values())
    used_generic = any(mode == "generic" for mode in topic_modes.values())
    
    if used_rag and not used_generic:
        badge = "🧠 Answer generated using your documents\n\n"
    elif used_generic and not used_rag:
        badge = "🌐 Answer generated using general knowledge\n\n"
    else:
        badge = "🔀 Answer generated using both documents and general knowledge\n\n"
    
    final_text = badge + final_text

    # Step 4: Update history
    if aggregate_mode:
        history = history_repository.add_to_history(" | ".join(topics), final_text, history)
    else:
        for t in topics:
            history = history_repository.add_to_history(t, topic_contents[t], history)

    # Step 5: Update dropdowns
    radio_choices, _ = history_formatter.create_history_choices(history)
    delete_choices = history_formatter.create_delete_choices(history)
    info_msg = get_history_info_message(len(history))

    print(f"✅ Multi-topic generation completed")
    print(f"{'='*60}\n")

    yield history, final_text, gr.update(choices=radio_choices, info=info_msg), gr.update(choices=delete_choices)
