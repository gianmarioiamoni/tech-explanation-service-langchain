# ui/utils/ui_messages.py
#
# UI message constants and formatting utilities
#
# Responsibilities:
# - Define UI message constants
# - Provide message formatting helpers

# -------------------------------
# Constants for UI messages
# -------------------------------
MSG_NO_CHATS = "📭 No chats saved"
MSG_ONE_CHAT = "💬 1 available chat - Open the dropdown to select a chat or a date"
MSG_MULTIPLE_CHATS = "💬 {count} available chats - Open the dropdown to select a chat or a date"


def get_history_info_message(history_count: int) -> str:
    """
    Generate appropriate info message based on history count.
    
    Args:
        history_count: Number of chats in history
        
    Returns:
        Formatted info message for the UI
    """
    if history_count == 0:
        return MSG_NO_CHATS
    elif history_count == 1:
        return MSG_ONE_CHAT
    else:
        return MSG_MULTIPLE_CHATS.format(count=history_count)

