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
from app.services.rag.rag_service import RAGService
from ui.utils.ui_messages import get_history_info_message

# Domain service instances
explanation_service = ExplanationService()
rag_service = RAGService()             # RAG context-aware
output_formatter = OutputFormatter()
history_repository = HistoryRepository()
history_formatter = HistoryFormatter()


def explain_topic_stream(topic: str, history, history_mode: str, rag_uploaded_state=None):
    # Stream explanation with RAG support using uploaded documents.
    #
    # Args:
    #     topic: Technical topic(s) to explain (comma-separated for multiple)
    #     history: Current chat history
    #     history_mode: "Aggregate into one chat" or "Save each topic as a separate chat"
    #     rag_uploaded_state: Current uploaded documents / vector store for RAG
    #
    # Yields:
    #     Tuple of (history, output_text, history_dropdown_update, delete_dropdown_update)

    topic_clean = (topic or "").strip()
    if not topic_clean:
        yield history, "Please enter at least one technical topic.", gr.update(), gr.update()
        return

    print(f"\n{'='*60}")
    print(f"🚀 Multi-topic request: '{topic_clean}'")

    topics = output_formatter.parse_topics(topic_clean)
    topic_contents = {}
    aggregate_mode = history_mode == "Aggregate into one chat"

    for topic_name in topics:
        # Step 1: Use RAG with uploaded docs
        explanation = rag_service.explain_topic(topic_name, uploaded_state=rag_uploaded_state)

        # Step 2: Fallback on generic LLM if RAG returns empty
        if not explanation.strip():
            for _, accumulated_text in explanation_service.explain_multiple_stream(topic_name):
                explanation = accumulated_text

        explanation = output_formatter.sanitize_output(explanation)
        topic_contents[topic_name] = explanation

        # Step 3: Prepare text for streaming
        if aggregate_mode:
            accumulated_raw = output_formatter.aggregate_topics_output(topics, topic_contents)
        else:
            accumulated_raw = f"{topic_name}:\n\n{explanation}"

        yield history, accumulated_raw, gr.update(), gr.update()

    # Final aggregation
    final_text = output_formatter.aggregate_topics_output(topics, topic_contents)

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
