# ui/gradio_app.py
#
# Gradio UI for the Tech Explanation Service
#
# Responsibilities:
# - Define the Gradio UI layout and components
# - Wire up event handlers to callbacks
# - Launch the Gradio application
#
# Note: Business logic and callbacks are in separate modules:
# - app/services/tech_explanation_service.py (business logic)
# - ui/callbacks/ (Gradio event callbacks)
# - ui/utils/ (UI utilities and constants)

import sys
from pathlib import Path

# Add project root to path to allow import of 'app'
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gradio as gr

# Import callbacks
from ui.callbacks import (
    explain_topic_stream,
    initialize_history,
    load_selected_chat,
    delete_selected_chat,
    search_in_history,
)

# -------------------------------
# UI Layout and Components
# -------------------------------
with gr.Blocks(
    title="Tech Explanation Service",
    css="""
        #output_explanation textarea {
            scroll-behavior: smooth !important;
        }
        #output_explanation {
            height: auto !important;
        }
    """
) as demo:
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
                elem_id="output_explanation",
                autoscroll=True,
            )
            
            # Debug and autoscroll script
            gr.HTML("""
                <script>
                console.log('=== AUTOSCROLL DEBUG START ===');
                
                // Wait for page to fully load
                setTimeout(function() {
                    console.log('1️⃣ Checking if elem_id is applied...');
                    const elem = document.getElementById('output_explanation');
                    console.log('   Result:', elem ? '✅ FOUND' : '❌ NOT FOUND');
                    
                    if (elem) {
                        console.log('   Element:', elem);
                        console.log('   Element tagName:', elem.tagName);
                        console.log('   Element classes:', elem.className);
                        
                        console.log('2️⃣ Searching for textarea...');
                        const textarea = elem.querySelector('textarea');
                        console.log('   Result:', textarea ? '✅ FOUND' : '❌ NOT FOUND');
                        
                        if (textarea) {
                            console.log('   Textarea:', textarea);
                            console.log('   Initial scrollHeight:', textarea.scrollHeight);
                            console.log('   Initial scrollTop:', textarea.scrollTop);
                            
                            console.log('3️⃣ Starting autoscroll polling (every 50ms)...');
                            let pollCount = 0;
                            setInterval(function() {
                                const currentScrollHeight = textarea.scrollHeight;
                                const currentScrollTop = textarea.scrollTop;
                                
                                // Always scroll to bottom
                                textarea.scrollTop = textarea.scrollHeight;
                                
                                // Log every 100 polls (every 5 seconds)
                                pollCount++;
                                if (pollCount % 100 === 0) {
                                    console.log(`   Poll #${pollCount}: scrollHeight=${currentScrollHeight}, scrollTop=${currentScrollTop} -> ${textarea.scrollTop}`);
                                }
                            }, 50);
                            
                            console.log('✅ Autoscroll active!');
                        } else {
                            console.error('❌ TEXTAREA NOT FOUND');
                            console.log('   Available children:', elem.children);
                            console.log('   Trying to find ANY textarea...');
                            const anyTextarea = document.querySelector('textarea');
                            if (anyTextarea) {
                                console.log('   Found a textarea elsewhere:', anyTextarea);
                                console.log('   Parent:', anyTextarea.parentElement);
                            }
                        }
                    } else {
                        console.error('❌ ELEMENT WITH ID output_explanation NOT FOUND');
                        console.log('   Checking all elements with gradio classes...');
                        const allTextareas = document.querySelectorAll('textarea');
                        console.log('   Total textareas found:', allTextareas.length);
                        allTextareas.forEach((ta, i) => {
                            console.log(`   Textarea ${i}:`, ta);
                            console.log(`     Parent:`, ta.parentElement);
                            console.log(`     Parent ID:`, ta.parentElement?.id);
                        });
                    }
                }, 2000); // Wait 2 seconds instead of 1
                
                console.log('=== AUTOSCROLL DEBUG END ===');
                </script>
            """)

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
