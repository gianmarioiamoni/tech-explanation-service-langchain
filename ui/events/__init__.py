# ui/events/__init__.py
#
# Events package
#
# This package contains modular event wiring functions for Gradio UI

from ui.events.initialization import wire_initialization_events
from ui.events.rag_events import wire_rag_events
from ui.events.explanation_events import wire_explanation_events
from ui.events.history_events import wire_history_events
from ui.events.download_events import wire_download_events

__all__ = [
    "wire_initialization_events",
    "wire_rag_events",
    "wire_explanation_events",
    "wire_history_events",
    "wire_download_events",
]

