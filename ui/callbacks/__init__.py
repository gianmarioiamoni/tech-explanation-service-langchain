# ui/callbacks/__init__.py
#
# Gradio callbacks package
#
# This package contains all Gradio event callbacks organized by functionality

from ui.callbacks.explanation_callbacks import explain_topic_stream
from ui.callbacks.history_callbacks import (
    initialize_history,
    load_selected_chat,
    delete_selected_chat,
    clear_all_chats,
)
from ui.callbacks.search_callbacks import search_in_history
from ui.callbacks.auth_callbacks import (
    initialize_user_session,
    update_quota_display,
)

__all__ = [
    "explain_topic_stream",
    "initialize_history",
    "load_selected_chat",
    "delete_selected_chat",
    "clear_all_chats",
    "search_in_history",
    "initialize_user_session",
    "update_quota_display",
]

