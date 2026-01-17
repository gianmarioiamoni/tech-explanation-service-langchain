# ui/components/topic_section.py
#
# Topic input section components
#
# Responsibilities:
# - Create topic input textbox
# - Create multi-topic behavior radio
# - Create output textbox

import gradio as gr


def create_topic_section():
    # Create topic input section with mode selector and output
    #
    # Returns:
    #     Tuple of (topic_input, history_mode, output_box)
    
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
        lines=15,
        interactive=False,
        autoscroll=True,
    )
    
    return topic_input, history_mode, output_box

