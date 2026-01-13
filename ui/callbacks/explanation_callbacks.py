# ui/callbacks/explanation_callbacks.py
#
# Callbacks for topic explanation functionality
#
# Responsibilities:
# - Handle streaming explanation generation
# - Manage multi-topic vs single-topic modes
# - Update history after explanation

import gradio as gr
from app.services.tech_explanation_service import TechExplanationService
from ui.utils.ui_messages import get_history_info_message

# Service instance
service = TechExplanationService()


def explain_topic_stream(topic: str, history, history_mode: str):
    """
    Stream the explanation for one or more topics.
    
    Args:
        topic: Technical topic(s) to explain (comma-separated for multiple)
        history: Current chat history
        history_mode: "Aggregate into one chat" or "Save each topic as a separate chat"
        
    Yields:
        Tuple of (history, output_text, history_dropdown_update, delete_dropdown_update)
    """
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

