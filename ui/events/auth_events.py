# ui/events/auth_events.py
#
# Event wiring for authentication and quota display.
# Connects user session initialization and quota updates to UI events.
#

import gradio as gr
from ui.callbacks.auth_callbacks import initialize_user_session, update_quota_display


def wire_auth_events(demo, user_session_state, quota_display):
    # Wire authentication and quota display events
    #
    # Args:
    #     demo: Gradio Blocks instance
    #     user_session_state: gr.State for user session
    #     quota_display: gr.HTML/Markdown for quota status
    
    # Initialize user session on app load
    demo.load(
        fn=initialize_user_session,
        inputs=None,
        outputs=[user_session_state, quota_display],
    )

